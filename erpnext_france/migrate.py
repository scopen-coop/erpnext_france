# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe


def move_subledger_account_by_company():
	copy_subledger_account("Customer")
	copy_subledger_account("Supplier")


def copy_subledger_account(doctype):
	if not frappe.db.exists("Custom Field", doctype + "-subledger_account"):
		return

	for party in list(frappe.get_all(doctype)):
		doc = frappe.get_doc(doctype, party.name)

		if not doc.get("subledger_account"):
			continue

		if len(doc.get("accounts")) == 0:
			continue

		for partyAccount in doc.get("accounts"):
			row = frappe.get_doc("Party Account", partyAccount.name)

			if not row.subledger_account:
				row.subledger_account = doc.get("subledger_account")
				row.save()

	field_subledger_account = frappe.get_doc("Custom Field", doctype + "-subledger_account")

	if field_subledger_account:
		field_subledger_account.hidden = 1
		field_subledger_account.save()
