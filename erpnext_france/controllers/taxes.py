import frappe
from frappe import _
from erpnext.stock.get_item_details import get_uom_conv_factor
from frappe.utils import parse_json, flt
import json
from erpnext.controllers.taxes_and_totals import get_itemised_taxable_amount

def before_save(doc, method):
	# Verif before update
	update_ecopart_taxes_for_item(doc)


def update_ecopart_taxes_for_item(doc):
	if len(doc.items) == 0:
		return

	(
		taxes_map,
		item_wise_tax_detail_before_tva,
		item_wise_tax_detail_with_tva,
		item_wise_tax_detail_standard_tva,
		used_ecopart_accounts,
		used_vat_accounts
	) = create_ecopart_taxes_map(doc)

	account_to_delete = find_accounts_to_update_delete(doc, used_vat_accounts)
	# Remove not used Taxes
	for vat_account in account_to_delete:
		if vat_account:
			delete_ecopart_taxes(doc, vat_account)


	for vat_account in used_vat_accounts:
		if vat_account:
			create_update_ecopart_with_vat_taxes(
				doc,
				taxes_map,
				item_wise_tax_detail_before_tva,
				item_wise_tax_detail_with_tva,
				used_ecopart_accounts,
				vat_account
			)
			create_update_vat_taxes(doc, item_wise_tax_detail_standard_tva, vat_account)
		else:
			create_update_ecopart_without_vat_taxes(
				doc,
				item_wise_tax_detail_before_tva,
				taxes_map,
				used_ecopart_accounts
			)

	doc.taxes.sort(key=lambda tax_obj: tax_obj.charge_type in ["On Previous Row Amount", "On Previous Row Total"])
	# # Recharge des numéros de ligne
	for i, tax in enumerate(doc.taxes, start=1):
		tax.idx = i

	from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals
	calculate_taxes_and_totals(doc)


def create_update_ecopart_without_vat_taxes(doc, item_wise_tax_detail_before_tva, taxes_map, used_ecopart_accounts):
	for ecopart_account in used_ecopart_accounts:
		delete_ecopart_taxes(doc, ecopart_account)
		if ecopart_account in item_wise_tax_detail_before_tva:
			item_tax_wise = item_wise_tax_detail_before_tva[ecopart_account]
			total_tax = taxes_map[None][ecopart_account]
			create_update_ecotax(doc, ecopart_account, None, item_tax_wise, total_tax)


def find_accounts_to_update_delete(doc, used_vat_accounts):
	accounts_vat = []
	for tax in doc.taxes:
		if tax.charge_type == 'On Net Total':
			accounts_vat.append(tax.account_head)
			continue

	account_to_delete = list(set(accounts_vat) - set(used_vat_accounts))
	return account_to_delete


def create_ecopart_taxes_map(doc):
	used_ecopart_accounts = []
	used_vat_accounts = []
	item_map = {}
	taxes_map = {}
	taxes_itemised_map = {}

	for doc_item in doc.items:
		item = frappe.get_doc('Item', doc_item.item_code)

		vat_account = init_taxes_map_and_vat_account(doc, doc_item, item, taxes_map)

		if vat_account not in used_vat_accounts:
			used_vat_accounts.append(vat_account)

		if len(item.eco_part):
			create_item_and_tax_maps_with_ecopart(
				doc_item,
				item,
				taxes_itemised_map,
				taxes_map,
				vat_account,
				used_ecopart_accounts
			)

		create_item_and_tax_maps_without_ecopart(
			doc_item,
			item_map,
			vat_account,
		)

	(
		item_wise_tax_detail_before_tva,
		item_wise_tax_detail_standard_tva,
		item_wise_tax_detail_with_tva
	) = build_item_wise_taxes_map(
		item_map,
		taxes_itemised_map,
		taxes_map,
		used_ecopart_accounts,
		used_vat_accounts
	)

	return (
		taxes_map,
		item_wise_tax_detail_before_tva,
		item_wise_tax_detail_with_tva,
		item_wise_tax_detail_standard_tva,
		used_ecopart_accounts,
		used_vat_accounts
	)


def init_taxes_map_and_vat_account(doc, doc_item, item, taxes_map):
	vat_account = None
	if doc_item.item_tax_template:
		item_tax_template = frappe.get_doc('Item Tax Template', doc_item.item_tax_template)
		for tax in item_tax_template.taxes:
			if tax.tax_type not in taxes_map:
				taxes_map[tax.tax_type] = {}
			vat_account = tax.tax_type
	elif doc.taxes_and_charges:
		sales_taxes_and_charges_template = frappe.get_doc('Sales Taxes and Charges Template', doc.taxes_and_charges)
		for tax in sales_taxes_and_charges_template.taxes:
			if tax.account_head not in taxes_map:
				taxes_map[tax.account_head] = {}
			vat_account = tax.account_head
	elif len(item.taxes) > 0:
		item_tax_template = frappe.get_doc('Item Tax Template', item.taxes[0].get('item_tax_template'))

		for tax in item_tax_template.taxes:
			if tax.tax_type not in taxes_map:
				taxes_map[tax.tax_type] = {}
			vat_account = tax.tax_type
	return vat_account


def create_item_and_tax_maps_with_ecopart(
	doc_item,
	item,
	taxes_itemised_map,
	taxes_map,
	vat_account,
	used_ecopart_accounts
):
	for ecopart in item.eco_part:
		if (
			vat_account not in taxes_map
			or ecopart.sell_account not in taxes_map[vat_account]
		):
			taxes_map[vat_account] = {}
			taxes_map[vat_account][ecopart.sell_account] = 0

		if vat_account not in taxes_itemised_map:
			taxes_itemised_map[vat_account] = {}

		if ecopart.sell_account not in taxes_itemised_map[vat_account]:
			taxes_itemised_map[vat_account][ecopart.sell_account] = {}

		if doc_item.item_code not in taxes_itemised_map[vat_account][ecopart.sell_account]:
			taxes_itemised_map[vat_account][ecopart.sell_account][doc_item.item_code] = 0

		taxes_map[vat_account][ecopart.sell_account] += ecopart.amount * doc_item.qty
		taxes_itemised_map[vat_account][ecopart.sell_account][doc_item.item_code] += ecopart.amount * doc_item.qty

		if ecopart.sell_account not in used_ecopart_accounts:
			used_ecopart_accounts.append(ecopart.sell_account)

def create_item_and_tax_maps_without_ecopart(
	doc_item,
	item_map,
	vat_account,
):
	if vat_account not in item_map:
		item_map[vat_account] = {}

	if doc_item.item_code not in item_map[vat_account]:
		item_map[vat_account][doc_item.item_code] = 0

	item_map[vat_account][doc_item.item_code] += doc_item.amount



def build_item_wise_taxes_map(item_map, taxes_itemised_map, taxes_map, used_ecopart_accounts, used_vat_accounts):
	item_wise_tax_detail_standard_tva = {}
	item_wise_tax_detail_before_tva = {}
	item_wise_tax_detail_with_tva = {}
	for vat_account in used_vat_accounts:
		if vat_account not in taxes_map:
			continue

		if not vat_account in item_wise_tax_detail_with_tva:
			item_wise_tax_detail_with_tva[vat_account] = {}
			item_wise_tax_detail_standard_tva[vat_account] = {}

		tax_rate = frappe.get_value('Account', vat_account, 'tax_rate') or 0

		for ecopart_account in used_ecopart_accounts:
			if ecopart_account not in taxes_map[vat_account]:
				continue


			tax_itemised = taxes_itemised_map[vat_account][ecopart_account]

			if not ecopart_account in item_wise_tax_detail_with_tva[vat_account]:
				item_wise_tax_detail_with_tva[vat_account][ecopart_account] = {}

			if not ecopart_account in item_wise_tax_detail_before_tva:
				item_wise_tax_detail_before_tva[ecopart_account] = {}

			for item_key in tax_itemised.keys():
				item_wise_tax_detail_before_tva[ecopart_account][item_key] = tax_itemised[item_key]
				item_wise_tax_detail_with_tva[vat_account][ecopart_account][item_key] = [
					tax_rate,
					tax_itemised[item_key] * tax_rate / 100
				]
		for item_key in item_map[vat_account].keys():
			item_wise_tax_detail_standard_tva[vat_account][item_key] = [
				tax_rate,
				item_map[vat_account][item_key] * tax_rate / 100
			]

	return item_wise_tax_detail_before_tva, item_wise_tax_detail_standard_tva, item_wise_tax_detail_with_tva


def create_update_ecopart_with_vat_taxes(
		doc,
		taxes_map,
		item_wise_tax_detail_before_tva,
		item_wise_tax_detail_with_tva,
		used_ecopart_accounts,
		vat_account
):

	for ecopart_account in used_ecopart_accounts:
		if ecopart_account not in taxes_map[vat_account]:
			continue

		total_tax = taxes_map[vat_account][ecopart_account]

		# Check if tax already exists
		ecopart_tax = None
		ecopart_vat_tax = None

		for tax in doc.taxes:
			if (
					tax.charge_type == 'Actual'
					and tax.description == _('Eco Part')
					and tax.account_head == ecopart_account
			):
				ecopart_tax = tax
			elif tax.charge_type == 'On Previous Row Amount' and tax.account_head == vat_account:
				ecopart_vat_tax = tax

		if ecopart_account in item_wise_tax_detail_before_tva:
			item_tax_wise = item_wise_tax_detail_before_tva[ecopart_account]
			ecopart_tax = create_update_ecotax(doc, ecopart_account, ecopart_tax, item_tax_wise, total_tax)

		# Need to be done outside the for loop to get ecopart_tax.idx
		if (
				vat_account in item_wise_tax_detail_with_tva
				and ecopart_account in item_wise_tax_detail_with_tva[vat_account]
		):
			item_tax_wise = item_wise_tax_detail_with_tva[vat_account][ecopart_account]

			create_update_vat_on_ecotax(
				doc,
				ecopart_tax.idx,
				ecopart_vat_tax,
				total_tax,
				item_tax_wise,
				vat_account
			)


def create_update_vat_taxes(doc, item_wise_tax_detail_standard_tva, vat_account):
	vat_tax = None
	for tax in doc.taxes:
		if (
				tax.charge_type == 'On Net Total'
				and tax.account_head == vat_account
				and vat_account in item_wise_tax_detail_standard_tva
		):
			vat_tax = tax
	item_tax_wise = item_wise_tax_detail_standard_tva[vat_account]
	tax_amount = 0
	tax_rate = 0
	for item_code in item_tax_wise.keys():
		tax_amount += item_tax_wise[item_code][1]
		tax_rate = item_tax_wise[item_code][0]
	if not vat_tax:
		vat_tax = frappe.get_doc({
			'doctype': 'Sales Taxes and Charges',
			'charge_type': 'On Net Total',
			'description': str(vat_account),
			'account_head': vat_account,
			'parent': doc.name,
			'parenttype': doc.doctype,
			'tax_amount': tax_amount,
			'rate': tax_rate,
			'item_wise_tax_detail': json.dumps(item_tax_wise),
			'dont_recompute_tax': True,
		})
		doc.append("taxes", vat_tax)
	else:
		vat_tax.item_wise_tax_detail = json.dumps(item_tax_wise)
		vat_tax.dont_recompute_tax = True


def create_update_ecotax(doc, ecopart_account, ecopart_tax, item_tax_wise, total_tax):
	# Update existing tax rows if found
	if ecopart_tax:
		ecopart_tax.tax_amount = total_tax
		ecopart_tax.item_wise_tax_detail = json.dumps(item_tax_wise)
		ecopart_tax.dont_recompute_tax = True
	else:
		ecopart_tax = frappe.get_doc({
			'doctype': 'Sales Taxes and Charges',
			'charge_type': 'Actual',
			'description': _('Eco Part'),
			'account_head': ecopart_account,
			'tax_amount': total_tax,
			'parent': doc.name,
			'parenttype': doc.doctype,
			'item_wise_tax_detail': json.dumps(item_tax_wise),
			'dont_recompute_tax': True,
		})
		doc.append("taxes", ecopart_tax)
	return ecopart_tax


def create_update_vat_on_ecotax(
		doc,
		ecopart_tax_idx,
		ecopart_vat_tax,
		total_tax,
		item_tax_wise,
		vat_account
):
	tax_rate = frappe.get_value('Account', vat_account, 'tax_rate') or 0

	if ecopart_vat_tax:
		ecopart_vat_tax.tax_amount = total_tax * tax_rate / 100
		ecopart_vat_tax.item_wise_tax_detail = json.dumps(item_tax_wise)
		ecopart_vat_tax.row_id = ecopart_tax_idx
	else:
		ecopart_vat_tax = frappe.get_doc({
			'doctype': 'Sales Taxes and Charges',
			'charge_type': 'On Previous Row Amount',
			'description': _('Eco Part VAT: {0}'.format(str(tax_rate))),
			'account_head': vat_account,
			'tax_amount': total_tax * tax_rate / 100,
			'row_id': ecopart_tax_idx,
			'rate': tax_rate,
			'item_wise_tax_detail': json.dumps(item_tax_wise),
			'dont_recompute_tax': True,
			'parent': doc.name,
			'parenttype': doc.doctype
		})
		doc.append("taxes", ecopart_vat_tax)


def delete_ecopart_taxes(doc, vat_account):
	tax_rate = frappe.get_value('Account', vat_account, 'tax_rate')
	to_remove = []
	for taxe in doc.taxes:
		if (
			taxe.account_head == vat_account
			or taxe.description in [_('Eco Part'), _('Eco Part VAT: {0}'.format(str(tax_rate)))]
		):
			to_remove.append(taxe)

	# Ensure the removal actually happens
	for taxe in to_remove:
		doc.taxes.remove(taxe)

	if not doc.is_new():
		doc.db_update()


def update_itemised_tax_data(doc):
	if not doc.taxes:
		return

	itemised_tax = get_itemised_tax(doc.taxes, True)

	# Remove non tax fees
	tax_accounts = set(
		itemised_tax[item][tax].get("tax_account")
		for item in itemised_tax
		for tax in itemised_tax[item]
	)
	tax_accounts = frappe.get_all(
		"Account",
		filters={"name": ("in", list(tax_accounts)), "account_type": "Tax"},
		fields=["name", "account_number"],
	)
	valid_tax_accounts = [t.name for t in tax_accounts]
	account_numbers = {t.name: t.accounr_number for t in tax_accounts}

	valid_itemised_tax = {}
	for item in itemised_tax:
		valid_itemised_tax[item] = {}
		for tax in itemised_tax[item]:
			if itemised_tax[item][tax].get("tax_account") in valid_tax_accounts:
				valid_itemised_tax[item][tax] = itemised_tax[item][tax]

	for row in doc.items:
		if not row.item_code:
			continue

		tax_rate = 0.0
		item_tax_rate = {}
		item_specific_rates = []

		if row.item_tax_rate:
			item_tax_rate = frappe.parse_json(row.item_tax_rate)

		# First check if tax rate is present
		# If not then look up in item_wise_tax_detail
		if item_tax_rate and hasattr(item_tax_rate, "items"):
			for tax, tax_rate_detail in item_tax_rate.items():
				tax_rate += tax_rate_detail

		elif row.item_code and valid_itemised_tax.get(row.item_code):
			item_specific_rates = [
				tax
				for tax in valid_itemised_tax.get(row.item_code).items()
				if flt(tax[1].get("form_rate", 0)) != 0.0
			]

			tax_rate = sum(
				[
					tax.get("tax_rate", 0)
					* (-1 if tax.get("add_deduct_tax") == "Deduct" else 1)
					for d, tax in (
						item_specific_rates
						or valid_itemised_tax.get(row.item_code, {}).items()
				)
				]
			)

		meta = frappe.get_meta(row.doctype)
		if meta.has_field("tax_rate"):
			row.tax_rate = flt(tax_rate, row.precision("tax_rate"))
			row.tax_amount = flt(
				(row.base_net_amount * tax_rate) / 100, row.precision("base_net_amount")
			)
			row.total_amount = flt(
				(row.base_net_amount + row.tax_amount), row.precision("total_amount")
			)

		row.item_tax_rate = json.dumps(
			[
				{
					"account": tax.get("tax_account"),
					"account_number": account_numbers.get(tax.get("tax_account")),
					"rate": tax.get("tax_rate", 0),
					"taxable_amount": row.get("base_net_amount"),
					"tax_amount": row.get("tax_amount"),
				}
				for d, tax in (
					item_specific_rates
					or valid_itemised_tax.get(row.item_code, {}).items()
			)
			]
		)


def get_itemised_tax_breakup_data(doc):
	itemised_tax = get_itemised_tax(doc.taxes)

	itemised_taxable_amount = get_itemised_taxable_amount(doc.items)
	itemised_tax_data = []
	for item_code, taxes in itemised_tax.items():
		itemised_tax_data.append(
			frappe._dict(
				{"item": item_code, "taxable_amount": itemised_taxable_amount.get(item_code, 0), **taxes}
			)
		)

	return itemised_tax_data


def get_itemised_tax(taxes, with_tax_account=False):
	itemised_tax = {}
	for tax in taxes:
		if getattr(tax, "category", None) and tax.category == "Valuation":
			continue

		item_tax_map = (
			json.loads(tax.item_wise_tax_detail) if tax.item_wise_tax_detail else {}
		)

		if item_tax_map:
			for item_code, tax_data in item_tax_map.items():
				itemised_tax.setdefault(item_code, frappe._dict())

				tax_rate = 0.0
				tax_amount = 0.0

				if isinstance(tax_data, list):
					tax_rate = flt(tax_data[0])
					tax_amount = flt(tax_data[1])
				else:
					tax_rate = flt(tax_data)

				if tax.charge_type == 'Actual':
					tax_amount = tax_rate
					tax_rate = 0.0

				if not tax_rate and tax_amount:
					tax_rate = flt(
						frappe.db.get_value("Account", tax.account_head, "tax_rate")
					)

				itemised_tax[item_code][tax.description] = frappe._dict(
					dict(
						tax_rate=tax_rate,
						tax_amount=tax_amount,
						add_deduct_tax=tax.get("add_deduct_tax"),
						form_rate=tax.rate,
					)
				)

				if with_tax_account:
					itemised_tax[item_code][
						tax.description
					].tax_account = tax.account_head

	return itemised_tax
