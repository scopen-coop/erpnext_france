# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
	add_custom_roles_for_reports()
	add_custom_roles_for_client_and_suppliers()

	set_accounting_journal_as_mandatory()

def make_custom_fields():
	create_custom_fields(custom_fields)

def add_custom_roles_for_reports():
	report_name = 'Fichier des Ecritures Comptables [FEC]'

	if not frappe.db.get_value('Custom Role', dict(report=report_name)):
		frappe.get_doc(dict(
			doctype='Custom Role',
			report=report_name,
			roles= [
				dict(role='Accounts Manager')
			]
		)).insert()

def set_accounting_journal_as_mandatory():
	frappe.db.set_single_value("Accounts Settings", "mandatory_accounting_journal", 1)
