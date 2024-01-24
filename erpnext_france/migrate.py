# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def move_subledger_account_by_company():
	copy_subledger_account('Customer')
	copy_subledger_account('Supplier')

# def add_custom_roles_for_reports():
# 	report_name = 'Fichier des Ecritures Comptables [FEC]'
#
# 	if not frappe.db.get_value('Custom Role', dict(report=report_name)):
# 		frappe.get_doc(dict(
# 			doctype='Custom Role',
# 			report=report_name,
# 			roles= [
# 				dict(role='Accounts Manager')
# 			]
# 		)).insert()
#

def copy_subledger_account(doctype):
	for seq, customer in enumerate(frappe.get_all(doctype)):
		doc = frappe.get_doc(doctype, customer.name)

		if not doc.subledger_account:
			continue

		if len(doc.accounts) == 0:
			continue

		for partyAccount in doc.accounts:
			row = frappe.get_doc("Party Account", partyAccount.name)

			if not row.subledger_account:
				row.subledger_account = doc.subledger_account
				row.save()

	field_subledger_account = frappe.get_last_doc('Custom Field', filters={'name': doctype + "-subledger_account"})

	if field_subledger_account:
		field_subledger_account.hidden = 1
		field_subledger_account.save()