# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
	add_custom_roles_for_reports()
	set_accounting_journal_as_mandatory()

# TODO : Trouver comment faire pour desactiver enable_onboarding juste après le wizard
# TODO : Actuellement c'est la dernière action qu'il effectue après avoir executé les hooks setup_wizard_*
# def after_wizard(args, args1):
# 	if frappe.db.get_single_value("System Settings", "enable_onboarding") == 1:
# 		frappe.db.set_single_value("System Settings", "enable_onboarding", 0)

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
