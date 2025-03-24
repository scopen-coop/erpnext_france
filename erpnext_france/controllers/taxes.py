import frappe
from frappe import _
from erpnext.stock.get_item_details import get_uom_conv_factor


def before_save(doc, method):
	# Verif before update
	update_ecopart_taxes_for_item(doc)


def update_ecopart_taxes_for_item(doc):
	taxes_map, used_ecopart_accounts, used_vat_accounts = create_ecopart_taxes_map(doc)
	account_to_delete, account_to_update = find_accounts_to_update_delete(doc, taxes_map, used_vat_accounts)

	# Remove not used Taxes
	for vat_account in account_to_delete:
		delete_ecopart_taxes(doc, vat_account)

	for vat_account in used_vat_accounts:
		if vat_account in taxes_map:
			create_update_ecopart_taxes(doc, taxes_map, used_ecopart_accounts, vat_account)

	# Recharge des numéros de ligne
	for i, tax in enumerate(doc.taxes, start=1):
		tax.idx = i

	from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals
	calculate_taxes_and_totals(doc)


def find_accounts_to_update_delete(doc, taxes_map, used_vat_accounts):
	account_to_update = []
	accounts_vat = []
	for tax in doc.taxes:
		if tax.charge_type == 'On Net Total':
			accounts_vat.append(tax.account_head)
			continue
		if tax.charge_type not in ('Actual', 'On Previous Row Amount'):
			continue

		for vat_tax in used_vat_accounts:
			tax_rate = frappe.get_value('Account', vat_tax, 'tax_rate')

			if vat_tax in taxes_map and taxes_map[vat_tax] and tax.description in _(
					'Eco Part {0}%'.format(str(tax_rate))):
				account_to_update.append(vat_tax)

	account_to_delete = list(set(accounts_vat) - set(used_vat_accounts))
	return account_to_delete, account_to_update


def create_ecopart_taxes_map(doc):
	used_ecopart_accounts = []
	used_vat_accounts = []
	taxes_map = {}
	for doc_item in doc.items:
		item = frappe.get_doc('Item', doc_item.item_code)

		if not len(item.eco_part):
			continue

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
			continue

		if tax_vat_account not in used_vat_accounts:
			used_vat_accounts.append(tax_vat_account)

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
		tax_rate = frappe.get_value('Account', vat_account, 'tax_rate')
		# Check if tax already exists
		existing_ecopart = None
		existing_vat = None

		for taxe in doc.taxes:
			if taxe.description == _('Eco Part {0}%'.format(str(tax_rate))) and taxe.account_head == ecopart_account:
				existing_ecopart = taxe
			elif taxe.description == _('Eco Part VAT: {0}'.format(str(tax_rate))) and taxe.account_head == vat_account:
				existing_vat = taxe

		# Update existing tax rows if found
		if existing_ecopart:
			existing_ecopart.tax_amount = total_tax
		else:
			existing_ecopart = frappe.get_doc({
				'doctype': 'Sales Taxes and Charges',
				'charge_type': 'Actual',
				'description': _('Eco Part {0}%'.format(str(tax_rate))),
				'account_head': ecopart_account,
				'tax_amount': total_tax,
				'parent': doc.name,
				'parenttype': doc.doctype
			})
			doc.append("taxes", existing_ecopart)

		if existing_vat:
			existing_vat.tax_amount = total_tax * tax_rate / 100
			existing_vat.row_id = existing_ecopart.idx
		else:
			existing_vat = frappe.get_doc({
				'doctype': 'Sales Taxes and Charges',
				'charge_type': 'On Previous Row Amount',
				'description': _('Eco Part VAT: {0}'.format(str(tax_rate))),
				'account_head': vat_account,
				'tax_amount': total_tax * tax_rate / 100,
				'row_id': existing_ecopart.idx,
				'rate': tax_rate,
				'parent': doc.name,
				'parenttype': doc.doctype
			})
			doc.append("taxes", existing_vat)


def delete_ecopart_taxes(doc, vat_account):
	tax_rate = frappe.get_value('Account', vat_account, 'tax_rate')
	to_remove = []
	for taxe in doc.taxes:
		if (
				taxe.account_head == vat_account
				or taxe.description in [_('Eco Part {0}%'.format(str(tax_rate))),
				                        _('Eco Part VAT: {0}'.format(str(tax_rate)))]
		):
			to_remove.append(taxe)

	# Ensure the removal actually happens
	for taxe in to_remove:
		doc.taxes.remove(taxe)

	doc.db_update()
