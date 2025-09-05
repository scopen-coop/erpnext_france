import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.utils import cint, flt

from erpnext_france.controllers.accounts_controller import get_down_payment_item_default
from erpnext_france.controllers.taxes import create_ecopart_taxes_map


@frappe.whitelist()
def init_down_payment_invoice(order_name, values):
	if isinstance(values, str):
		values = frappe.parse_json(values)

	order = frappe.get_cached_doc("Sales Order", order_name)

	if not order.get("project") and "project" in values:
		order.project = values["project"]

	down_payment_invoice = frappe.get_cached_doc(
		{
			"doctype": "Sales Invoice",
			"customer": order.customer,
			"customer_name": order.customer,
			"contact_person": order.contact_person,
			"project": order.project,
			"transaction_date": frappe.utils.getdate(),
			"is_down_payment_invoice": 1,
		}
	)

	tva_accounting_on_down_payment = frappe.db.get_single_value(
		"ERPNext France Settings", "tva_accounting_on_down_payment"
	)
	if not tva_accounting_on_down_payment:
		add_down_payment_without_tva(order, down_payment_invoice, values)
	else:
		add_down_payment_with_tva(order, down_payment_invoice, values)

	# Insère le down_payment_invoice dans la base de données
	down_payment_invoice.insert()

	return down_payment_invoice.name


def add_down_payment_without_tva(order, down_payment_invoice, values):
	total = order.grand_total
	down_payment_items = frappe.get_all("Item", filters={"is_down_payment_item": 1})
	if len(down_payment_items) == 0:
		frappe.throw(_("Cannot find Deposit Item, may be missing Item with checkbox Is Down Payment"))
		return

	down_payment_item = frappe.get_cached_doc("Item", down_payment_items[0].name)
	income_account = get_down_payment_item_default(down_payment_item.item_code)

	if not income_account or income_account == "":
		frappe.throw(
			_("Cannot find Deposit Item, may be missing Default Accountancy table with Income Account")
		)
		return

	docitem = frappe.new_doc("Sales Invoice Item")
	docitem.item_code = down_payment_item.name
	docitem.sales_order = order.name

	if values.down_payment_type == "ByPercent":
		if float(values.down_payment_value) > 0:
			docitem.rate = float(total) * float(values.down_payment_value) / 100
		else:
			docitem.rate = float(total) * float(down_payment_item.down_payment_percentage) / 100
	else:
		docitem.rate = float(values.down_payment_value) or 0

	docitem.qty = 1
	docitem.amount = docitem.rate
	docitem.uom = down_payment_item.stock_uom
	docitem.conversion_factor = 1
	docitem.income_account = income_account
	docitem.down_payment_rate = down_payment_item.down_payment_percentage

	down_payment_invoice.append("items", docitem)


def add_down_payment_with_tva(order, down_payment_invoice, values):
	down_payment_items = frappe.get_all("Item", filters={"is_down_payment_item": 1})
	if len(down_payment_items) == 0:
		frappe.throw(_("Cannot find Deposit Item, may be missing Item with checkbox Is Down Payment"))
		return

	down_payment_item = frappe.get_cached_doc("Item", down_payment_items[0].name)
	income_account = get_down_payment_item_default(down_payment_item.item_code)

	if not income_account or income_account == "":
		frappe.throw(
			_("Cannot find Deposit Item, may be missing Default Accountancy table with Income Account")
		)
		return

	down_payments_item_map = []
	for order_item in order.items:
		item = frappe.get_cached_doc("Item", order_item.item_code)
		get_item_tax_template(order, order_item, item, down_payments_item_map)

	group_down_payments_item_map = {}
	for down_payments_item_info in down_payments_item_map:
		if down_payments_item_info.get("item_tax_template") not in group_down_payments_item_map.keys():
			group_down_payments_item_map[down_payments_item_info.get("item_tax_template")] = 0
		group_down_payments_item_map[
			down_payments_item_info.get("item_tax_template")
		] += down_payments_item_info.get("amount")

	total = order.grand_total
	new_discount_percent = None
	if values.down_payment_type == "ByAmount" and float(total) != 0:
		new_discount_percent = float(values.down_payment_value) / float(total)

	for item_tax_template in group_down_payments_item_map.keys():
		docitem = frappe.new_doc("Sales Invoice Item")
		docitem.item_code = down_payment_item.name
		docitem.sales_order = order.name

		if values.down_payment_type == "ByPercent":
			if float(values.down_payment_value) > 0:
				docitem.rate = (
					float(group_down_payments_item_map[item_tax_template])
					* float(values.down_payment_value)
					/ 100
				)
			else:
				docitem.rate = (
					float(group_down_payments_item_map[item_tax_template])
					* float(down_payment_item.down_payment_percentage)
					/ 100
				)
		else:
			docitem.rate = float(group_down_payments_item_map[item_tax_template]) * new_discount_percent

		docitem.qty = 1
		docitem.amount = docitem.rate
		docitem.uom = down_payment_item.stock_uom
		docitem.conversion_factor = 1
		docitem.income_account = income_account
		docitem.down_payment_rate = down_payment_item.down_payment_percentage
		docitem.item_tax_template = item_tax_template
		down_payment_invoice.append("items", docitem)


def get_item_tax_template(order, order_item, item, down_payments_item_map):
	item_tax_template_name = None
	if order_item.item_tax_template:
		item_tax_template = frappe.get_cached_doc("Item Tax Template", order_item.item_tax_template)
		item_tax_template_name = item_tax_template.name
	elif order.taxes_and_charges:
		taxes_and_charges_template = frappe.get_cached_doc(
			"Sales Taxes and Charges Template", order.taxes_and_charges
		)
		taxes_map = []
		for tax in taxes_and_charges_template.taxes:
			taxes_map.append(tax.account_head)
		item_tax_template_name = find_item_tax_template(taxes_map)
	elif len(item.taxes) > 0:
		item_tax_template = frappe.get_cached_doc("Item Tax Template", item.taxes[0].get("item_tax_template"))
		item_tax_template_name = item_tax_template.name
	else:
		frappe.throw(_("Item Tax template cannot be defined"))

	down_payments_item_map.append({"item_tax_template": item_tax_template_name, "amount": order_item.amount})


def find_item_tax_template(taxes_map):
	# Utilise le DocType pour la table enfant "Item Tax Template Tax"
	ItemTaxTemplateTax = DocType("Item Tax Template Detail")

	# Construit une requête pour obtenir les templates et leurs taxes_map
	query = (
		frappe.qb.from_(ItemTaxTemplateTax)
		.select(ItemTaxTemplateTax.parent.as_("template_name"), ItemTaxTemplateTax.tax_type)
		.where(ItemTaxTemplateTax.tax_type.isin(taxes_map))
	)

	result = query.run(as_dict=True)

	# Compte les taxes_map uniques par template
	from collections import defaultdict

	template_tax_counts = defaultdict(set)

	for row in result:
		template_tax_counts[row.template_name].add(row.tax_type)

	# Trouve les templates qui contiennent tous les taxes_map recherchés
	matching_templates = []
	for template, tax_set in template_tax_counts.items():
		if set(taxes_map).issubset(tax_set):
			matching_templates.append(template)

	tax_template_name = None
	if len(matching_templates) > 0:
		tax_template_name = matching_templates[0]
	else:
		frappe.throw(_("Missing Item Tax Template Corresponding to Sales Taxes and Charges Template"))

	return tax_template_name


def set_paid_amount_of_linked_invoice(doc, method):
	if doc.get("references")[0].get("reference_doctype") != "Sales Invoice":
		return

	sales_invoice = frappe.get_cached_doc("Sales Invoice", doc.get("references")[0].get("reference_name"))

	if sales_invoice.get("is_down_payment_invoice") == 1:
		return

	paid_amount = 0.0
	base_paid_amount = 0.0
	for data in sales_invoice.payments:
		data.base_amount = flt(
			data.amount * sales_invoice.conversion_rate, sales_invoice.precision("base_paid_amount")
		)
		paid_amount += data.amount
		base_paid_amount += data.base_amount

	for advance in sales_invoice.get("advances"):
		if advance.reference_type == "Payment Entry":
			paid_amount += advance.advance_amount
			base_paid_amount += advance.advance_amount

	sales_invoice.outstanding_amount = flt(
		sales_invoice.rounded_total - (paid_amount + doc.paid_amount),
		sales_invoice.precision("outstanding_amount"),
	)

	if flt(sales_invoice.outstanding_amount) == 0:
		sales_invoice.set_status(update=True)

	sales_invoice.save(ignore_permissions=True)
