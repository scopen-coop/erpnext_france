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


def migrate_due_date_based_on_france():
	payment_terms = frappe.get_all(
		"Payment Term", fields=["name", "due_date_based_on", "custom_due_date_based_on_france"]
	)
	for payment_term in payment_terms:
		if payment_term.get("custom_due_date_based_on_france") is None and payment_term.get(
			"due_date_based_on"
		):
			frappe.db.set_value(
				"Payment Term",
				payment_term.name,
				"custom_due_date_based_on_france",
				payment_term.due_date_based_on,
			)


def update_worker_timeout():
	_sirene_worker_timeout = 3600

	"""S'assure que le timeout worker est suffisant pour le job cron SIRENE"""
	from frappe.installer import update_site_config

	site_config = frappe.get_site_config()
	workers = site_config.get("workers", {})
	default_timeout = workers.get("default", {}).get("timeout", 300)

	if default_timeout < _sirene_worker_timeout:
		update_site_config(
			"workers",
			{"default": {"timeout": _sirene_worker_timeout}, "short": {"timeout": _sirene_worker_timeout}},
		)
		print("Worker timeout mis à jour à 3600s pour le job SIRENE")
