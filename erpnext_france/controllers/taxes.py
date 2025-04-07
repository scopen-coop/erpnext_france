import frappe
from frappe import _
from erpnext.stock.get_item_details import get_uom_conv_factor


def before_save(doc, method):
	# Verif before update
	update_ecopart_taxes_for_item(doc)


def update_ecopart_taxes_for_item(doc):
	if len(doc.items) == 0:
		return

	taxes_map, used_ecopart_accounts, used_vat_accounts = create_ecopart_taxes_map(doc)
	account_to_delete = find_accounts_to_update_delete(doc, used_vat_accounts)

	# Remove not used Taxes
	for vat_account in account_to_delete:
		if vat_account:
			delete_ecopart_taxes(doc, vat_account)

	for vat_account in used_vat_accounts:
		if vat_account:
			create_update_ecopart_taxes(doc, taxes_map, used_ecopart_accounts, vat_account)
			create_other_vat_taxes(doc, vat_account)

	# Recharge des numéros de ligne
	for i, tax in enumerate(doc.taxes, start=1):
		tax.idx = i

	from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals
	calculate_taxes_and_totals(doc)


def create_other_vat_taxes(doc, vat_account):
	origin_vat_tax = None
	account = frappe.get_doc('Account', vat_account)
	for taxe in doc.taxes:
		if (
				taxe.charge_type == 'On Net Total'
				and taxe.account_head == vat_account
		):
			origin_vat_tax = taxe
			if taxe.rate != account.tax_rate:
				taxe.rate = account.tax_rate

	if not origin_vat_tax:
		origin_vat_tax = frappe.get_doc({
			'doctype': 'Sales Taxes and Charges',
			'charge_type': 'On Net Total',
			'description': str(vat_account),
			'account_head': vat_account,
			'rate': account.tax_rate,
			'parent': doc.name,
			'parenttype': doc.doctype
		})
		doc.append("taxes", origin_vat_tax)


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
	taxes_map = {}
	for doc_item in doc.items:
		item = frappe.get_doc('Item', doc_item.item_code)

		tax_vat_account = None
		if doc_item.item_tax_template:
			item_tax_template = frappe.get_doc('Item Tax Template', doc_item.item_tax_template)
			for tax in item_tax_template.taxes:
				if tax.tax_type not in taxes_map:
					taxes_map[tax.tax_type] = {}
				tax_vat_account = tax.tax_type
		elif doc.taxes_and_charges:
			sales_taxes_and_charges_template = frappe.get_doc('Sales Taxes and Charges Template', doc.taxes_and_charges)
			for tax in sales_taxes_and_charges_template.taxes:
				if tax.account_head not in taxes_map:
					taxes_map[tax.account_head] = {}
				tax_vat_account = tax.account_head
		else:
			if len(item.taxes) > 0:
				item_tax_template = frappe.get_doc('Item Tax Template', item.taxes[0].get('item_tax_template'))

				for tax in item_tax_template.taxes:
					if tax.tax_type not in taxes_map:
						taxes_map[tax.tax_type] = {}
					tax_vat_account = tax.tax_type

		if tax_vat_account not in used_vat_accounts:
			used_vat_accounts.append(tax_vat_account)

		if not len(item.eco_part):
			continue

		for ecopart in item.eco_part:
			if (
					tax_vat_account not in taxes_map
					or ecopart.sell_account not in taxes_map[tax_vat_account]
			):
				taxes_map[tax_vat_account] = {}
				taxes_map[tax_vat_account][ecopart.sell_account] = 0
			taxes_map[tax_vat_account][ecopart.sell_account] += ecopart.amount * doc_item.qty

			if ecopart.sell_account not in used_ecopart_accounts:
				used_ecopart_accounts.append(ecopart.sell_account)

	return taxes_map, used_ecopart_accounts, used_vat_accounts


def create_update_ecopart_taxes(doc, taxes_map, used_ecopart_accounts, vat_account):
	for ecopart_account in used_ecopart_accounts:
		if ecopart_account not in taxes_map[vat_account]:
			continue

		total_tax = taxes_map[vat_account][ecopart_account]
		tax_rate = frappe.get_value('Account', vat_account, 'tax_rate') or 0

		# Check if tax already exists
		origin_vat_tax = None
		ecopart_tax = None
		ecopart_vat_tax = None

		for taxe in doc.taxes:
			if (
					taxe.charge_type == 'Actual'
					and taxe.description == _('Eco Part')
					and taxe.account_head == ecopart_account
			):
				ecopart_tax = taxe
			elif taxe.charge_type == 'On Previous Row Amount' and taxe.account_head == vat_account:
				ecopart_vat_tax = taxe
			elif taxe.charge_type == 'On Net Total' and taxe.account_head == vat_account:
				origin_vat_tax = taxe

		if not origin_vat_tax and vat_account:
			origin_vat_tax = frappe.get_doc({
				'doctype': 'Sales Taxes and Charges',
				'charge_type': 'On Net Total',
				'description': str(vat_account),
				'account_head': vat_account,
				'parent': doc.name,
				'parenttype': doc.doctype
			})
			doc.append("taxes", origin_vat_tax)

		# Update existing tax rows if found
		if ecopart_tax:
			ecopart_tax.tax_amount = total_tax
		else:
			ecopart_tax = frappe.get_doc({
				'doctype': 'Sales Taxes and Charges',
				'charge_type': 'Actual',
				'description': _('Eco Part'),
				'account_head': ecopart_account,
				'tax_amount': total_tax,
				'parent': doc.name,
				'parenttype': doc.doctype
			})
			doc.append("taxes", ecopart_tax)

		if tax_rate:
			if ecopart_vat_tax:
				ecopart_vat_tax.tax_amount = total_tax * tax_rate / 100
				ecopart_vat_tax.row_id = ecopart_tax.idx
			else:
				ecopart_vat_tax = frappe.get_doc({
					'doctype': 'Sales Taxes and Charges',
					'charge_type': 'On Previous Row Amount',
					'description': _('Eco Part VAT: {0}'.format(str(tax_rate))),
					'account_head': vat_account,
					'tax_amount': total_tax * tax_rate / 100,
					'row_id': ecopart_tax.idx,
					'rate': tax_rate,
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
