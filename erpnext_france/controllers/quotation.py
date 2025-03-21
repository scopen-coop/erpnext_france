import frappe
from frappe import _
from erpnext.stock.get_item_details import get_uom_conv_factor


def on_update(doc, method):
	# old_doc = doc.get_doc_before_save()
	# if not old_doc:
	# 	return

	# Verif before update
	update_ecopart_taxes_for_item(doc)

def update_ecopart_taxes_for_item(doc):
	taxes_map = {
		'DEEE': {},
		'PMCB': {}
	}

	used_ecopart_accounts = []
	used_vat_accounts = []
	for ecotax_type in ('DEEE', 'PMCB'):
		for doc_item in doc.items:
			item = frappe.get_doc('Item', doc_item.item_code)

			if not len(item.eco_part):
				continue

			tax_vat_account = None
			if doc_item.item_tax_template:
				item_tax_template = frappe.get_doc('Item Tax Template', doc_item.item_tax_template)
				for tax in item_tax_template.taxes:
					if tax.tax_type not in taxes_map[ecotax_type]:
						taxes_map[ecotax_type][tax.tax_type] = {}
					tax_vat_account = tax.tax_type
			elif doc.taxes_and_charges:
				sales_taxes_and_charges_template = frappe.get_doc('Sales Taxes and Charges Template', doc.taxes_and_charges)
				for tax in sales_taxes_and_charges_template.taxes:
					if tax.account_head not in taxes_map[ecotax_type]:
						taxes_map[ecotax_type][tax.account_head] = {}
					tax_vat_account = tax.account_head
			else:
				continue

			if tax_vat_account not in used_vat_accounts:
				used_vat_accounts.append(tax_vat_account)

			for eco_part in item.eco_part:
				if ecotax_type != eco_part.tax_type:
					continue
				if (
					tax_vat_account not in taxes_map[eco_part.tax_type]
					or eco_part.sell_account not in taxes_map[eco_part.tax_type][tax_vat_account]
				):
					taxes_map[eco_part.tax_type][tax_vat_account] = {}
					taxes_map[eco_part.tax_type][tax_vat_account][eco_part.sell_account] = 0
				taxes_map[eco_part.tax_type][tax_vat_account][eco_part.sell_account] += eco_part.amount * doc_item.qty

				if eco_part.sell_account not in used_ecopart_accounts:
					used_ecopart_accounts.append(eco_part.sell_account)

	account_to_update = []
	account_to_delete = []
	account_to_append = used_ecopart_accounts
	for tax in doc.taxes:
		if tax.charge_type != 'Actual':
			continue
		if tax.account_head in used_ecopart_accounts:
			account_to_append.remove(tax.account_head)
			account_to_update.append(tax.account_head)
		else:
			account_to_delete.append(tax.account_head)

	for vat_account in used_vat_accounts:
		for ecopart_account in account_to_append:
			total_tax = 0
			if vat_account not in taxes_map[ecotax_type]:
				continue

			for ecotax_type in ('DEEE', 'PMCB'):
				if ecopart_account in taxes_map[ecotax_type][vat_account]:
					total_tax += taxes_map[ecotax_type][vat_account][ecopart_account]

			tax_rate = frappe.get_value('Account', vat_account, 'tax_rate')

			ecopart_sales_taxes_and_charges = frappe.get_doc({
				'doctype': 'Sales Taxes and Charges',
				'charge_type': 'Actual',
				'description': _('Eco Part {0}%'.format(str(tax_rate))),
				'account_head': ecopart_account,
				'tax_amount': total_tax,
				'parent': doc.name,
				'parenttype': doc.doctype
			})


			ecopart_sales_taxes_and_charges.insert()
			doc.append("taxes", ecopart_sales_taxes_and_charges)

			i = 1
			for taxe in doc.taxes:
				if taxe.name == ecopart_sales_taxes_and_charges.name:
					break
				i += 1


			vat_sales_taxes_and_charges = frappe.get_doc({
				'doctype': 'Sales Taxes and Charges',
				'charge_type': 'On Previous Row Amount',
				'description': _('Eco Part VAT: {0}'.format(vat_account)),
				'account_head': vat_account,
				'tax_amount': total_tax * tax_rate / 100,
				'row_id': i,
				'rate': tax_rate,
				'parent': doc.name,
				'parenttype': doc.doctype
			})

			vat_sales_taxes_and_charges.insert()
			doc.append("taxes", vat_sales_taxes_and_charges)

	for vat_account in used_vat_accounts:
		for ecopart_account in account_to_update:
			total_tax = 0
			if vat_account not in taxes_map[ecotax_type]:
				continue

			for ecotax_type in ('DEEE', 'PMCB'):
				if ecopart_account in taxes_map[ecotax_type][vat_account]:
					total_tax += taxes_map[ecotax_type][vat_account][ecopart_account]
			# frappe.throw(str(taxes_map))
			tax_rate = frappe.get_value('Account', vat_account, 'tax_rate')

			ecopart_sales_taxes_and_charges = None
			row_id = 1
			for taxe in doc.taxes:
				if taxe.description == _('Eco Part {0}%'.format(str(tax_rate))):
					ecopart_sales_taxes_and_charges = taxe
					break
				row_id += 1

			if not ecopart_sales_taxes_and_charges:
				continue

			ecopart_sales_taxes_and_charges.tax_amount = total_tax
			ecopart_sales_taxes_and_charges.save()

			vat_sales_taxes_and_charges = None
			for taxe in doc.taxes:
				if taxe.description == _('Eco Part VAT: {0}'.format(str(tax_rate))):
					vat_sales_taxes_and_charges = taxe
					break

			if not vat_sales_taxes_and_charges:
				continue

			vat_sales_taxes_and_charges.row_id = row_id
			vat_sales_taxes_and_charges.save()

	# # Remove not used Taxes
	# for vat_account in used_vat_accounts:
	# 	tax_rate = frappe.get_value('Account', vat_account, 'tax_rate')
	# 	ecopart_sales_taxes_and_charges = None
	# 	row_id = 1
	# 	for taxe in doc.taxes:
	# 		if taxe.description == _('Eco Part {0}%'.format(str(tax_rate))):
	# 			ecopart_sales_taxes_and_charges = taxe
	# 			break
	# 		row_id += 1
	#
	# 	if not ecopart_sales_taxes_and_charges:
	# 		continue
	#
	# 	vat_sales_taxes_and_charges = None
	# 	for taxe in doc.taxes:
	# 		if taxe.description == _('Eco Part VAT: {0}'.format(str(tax_rate))):
	# 			vat_sales_taxes_and_charges = taxe
	# 			break
	#
	# 	if ecopart_sales_taxes_and_charges:
	# 		doc.taxes.remove(ecopart_sales_taxes_and_charges)
	# 	if vat_sales_taxes_and_charges:
	# 		doc.taxes.remove(vat_sales_taxes_and_charges)


	from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals
	calculate_taxes_and_totals(doc)
