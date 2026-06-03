# Copyright (c) 2025, Scopen and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, flt

from erpnext_france.controllers.accounts_controller import get_down_payment_item_default
from erpnext_france.controllers.taxes import find_item_tax_template


@frappe.whitelist()
def init_down_payment_invoice(order_name, values):
	if isinstance(values, str):
		values = frappe.parse_json(values)

	order = frappe.get_cached_doc("Sales Order", order_name)

	if not order.get("project") and "project" in values:
		order.project = values["project"]

	if values.down_payment_type == "ByPercent":
		if 0 > values.down_payment_value or values.down_payment_value > 100:
			frappe.throw("Down Payment By Percent should be between 0 and 100")
		if not float(values.down_payment_value).is_integer():
			frappe.throw("Down Payment By Percent should be an integer")

	if values.down_payment_type == "ByAmount" and (
		0 > values.down_payment_value or values.down_payment_value > order.grand_total
	):
		frappe.throw("Down Payment By Amount should be between 0 and total")

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

	down_payment_invoice.down_payment_value = values.down_payment_value
	down_payment_invoice.down_payment_type = values.down_payment_type

	if (
		values.down_payment_type == "ByAmount"
		and values.down_payment_value != down_payment_invoice.grand_total
	):
		down_payment_invoice.disable_rounded_total = 1

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
		docitem.rate = float(total) * float(values.down_payment_value) / 100
		docitem.description = _("Down Payment {0} {1} on Sales Order {2} {3} € HT").format(
			str(values.down_payment_value),
			"%",
			str(order.name),
			str(docitem.rate),
		)
	else:
		docitem.rate = float(values.down_payment_value)
		docitem.description = _("Down Payment {0} {1} on Sales Order {2} {3} € HT").format(
			str(docitem.rate),
			"€",
			str(order.name),
			frappe.format_value(docitem.rate, {"fieldtype": "Currency"}),
		)

	docitem.qty = 1
	docitem.amount = docitem.rate
	docitem.uom = down_payment_item.stock_uom
	docitem.conversion_factor = 1
	docitem.income_account = income_account
	docitem.down_payment_rate = values.down_payment_value
	docitem.discount_amount = 0

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
	new_discount_percent = 0
	if values.down_payment_type == "ByAmount" and float(total) != 0:
		new_discount_percent = 100 * float(values.down_payment_value) / float(total)
	elif values.down_payment_type == "ByPercent":
		if float(values.down_payment_value) > 0:
			new_discount_percent = float(values.down_payment_value)

	for item_tax_template in group_down_payments_item_map.keys():
		docitem = frappe.new_doc("Sales Invoice Item")
		docitem.item_code = down_payment_item.name
		docitem.sales_order = order.name

		if values.down_payment_type == "ByPercent":
			docitem.rate = (
				float(group_down_payments_item_map[item_tax_template]) * float(new_discount_percent) / 100
			)

			docitem.description = _("Down Payment {0} {1} on Sales Order {2} {3} € HT").format(
				values.down_payment_value,
				"%",
				str(order.name),
				frappe.format_value(docitem.rate, {"fieldtype": "Currency"}),
			)
		else:
			docitem.rate = float(group_down_payments_item_map[item_tax_template]) * new_discount_percent / 100
			docitem.description = _("Down Payment {0} {1} on Sales Order {2} {3} € HT").format(
				values.down_payment_value,
				"€",
				str(order.name),
				frappe.format_value(docitem.rate, {"fieldtype": "Currency"}),
			)

		docitem.qty = 1
		docitem.amount = docitem.rate
		docitem.uom = down_payment_item.stock_uom
		docitem.conversion_factor = 1
		docitem.income_account = income_account
		docitem.discount_amount = 0
		docitem.down_payment_rate = new_discount_percent
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


def set_paid_amount_of_linked_invoice(doc, method):
	"""Recalculate Sales Invoice outstanding only for down-payment final invoices.

	For regular invoices, ERPNext already updates outstanding from Payment Ledger
	Entries on Payment Entry submit. Recomputing here double-counts the payment and
	can drive outstanding_amount negative (e.g. after SEPA acceptance).
	"""
	if doc.payment_type != "Receive":
		return

	for reference in doc.get("references", []):
		if reference.reference_doctype != "Sales Invoice":
			continue

		sales_invoice = frappe.get_doc("Sales Invoice", reference.reference_name)

		if sales_invoice.get("is_down_payment_invoice") == 1:
			continue

		if not _has_down_payment_advances(sales_invoice):
			continue

		outstanding_amount = _calculate_sales_invoice_outstanding(sales_invoice, doc, reference)

		sales_invoice.outstanding_amount = outstanding_amount
		if flt(outstanding_amount) == 0:
			sales_invoice.set_status(update=True, update_modified=False)

		# Avoid full save(): it reloads payment schedule rows and tries to reset
		# "outstanding" from payment_amount, which is not allow_on_submit.
		sales_invoice.db_set("outstanding_amount", outstanding_amount, update_modified=False)


def _has_down_payment_advances(sales_invoice):
	return any(
		cint(advance.is_down_payment)
		for advance in sales_invoice.get("advances") or []
		if advance.reference_type == "Payment Entry"
	)


def _calculate_sales_invoice_outstanding(sales_invoice, payment_entry, reference):
	paid_amount = sum(flt(payment.amount) for payment in sales_invoice.payments or [])

	for advance in sales_invoice.get("advances") or []:
		if advance.reference_type == "Payment Entry":
			paid_amount += flt(advance.allocated_amount or advance.advance_amount)

	# Payment Entry allocations are not stored on the invoice advances table.
	if not _is_payment_entry_in_advances(sales_invoice, payment_entry.name):
		paid_amount += flt(reference.allocated_amount)

	invoice_total = flt(sales_invoice.rounded_total or sales_invoice.grand_total)
	outstanding_amount = flt(
		invoice_total - paid_amount,
		sales_invoice.precision("outstanding_amount"),
	)

	return max(0, outstanding_amount)


def _is_payment_entry_in_advances(sales_invoice, payment_entry_name):
	return any(
		advance.reference_type == "Payment Entry" and advance.reference_name == payment_entry_name
		for advance in sales_invoice.get("advances") or []
	)
