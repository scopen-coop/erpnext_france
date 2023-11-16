# Copyright (c) 2019, Dokos SAS and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.email.doctype.notification.notification import get_context
from frappe.model.document import Document

from erpnext_france.controllers.general_ledger import make_entry, make_reverse_gl_entries


class AccountingJournal(Document):
	def validate(self):
		if self.conditions:
			self.validate_conditions()

	def validate_conditions(self):
		for condition in self.conditions:
			if condition.condition:
				temp_doc = frappe.new_doc(condition.document_type)
				try:
					frappe.safe_eval(condition.condition, None, get_context(temp_doc))
				except Exception:
					frappe.throw(_("The Condition '{0}' is invalid").format(condition))


@frappe.whitelist()
def get_entries(doctype, docnames):
	return frappe.get_list(
		"GL Entry",
		filters={
			"voucher_type": doctype,
			"voucher_no": ("in", frappe.parse_json(docnames)),
			"is_cancelled": 0,
		},
		fields=[
			"name",
			"account",
			"debit",
			"credit",
			"accounting_journal",
			"voucher_no",
			"account_currency",
		],
	)


# @dokos
@frappe.whitelist()
def accounting_journal_adjustment(doctype, docnames, accounting_journal):
	for docname in frappe.parse_json(docnames):
		original_entries = frappe.get_all(
			"GL Entry",
			fields=["*"],
			filters={"voucher_type": doctype, "voucher_no": docname, "is_cancelled": 0},
		)

		make_reverse_gl_entries(
			voucher_type=doctype, voucher_no=docname, cancel_payment_ledger_entries=False
		)

		for gl_entry in original_entries:
			gl_entry["name"] = None
			gl_entry["accounting_journal"] = accounting_journal
			make_entry(gl_entry, False, "No")


@frappe.whitelist()
def get_accounting_journal(doc):
	doc = frappe.parse_json(doc)

	applicable_rules = []
	query_filters = {
		"company": doc.get("company"),
		"disabled": 0,
		"document_type": doc.get("doctype"),
	}

	if doc.get("doctype") == "Payment Entry":
		query_filters["account"] = (
			doc.get("paid_to") if doc.get("payment_type") == "Receive" else doc.get("paid_from")
		)

	applicable_rules = frappe.get_all(
		"Accounting Journal",
		filters=query_filters,
		fields=[
			"name",
			"type",
			"account",
			"`tabAccounting Journal Rule`.document_type",
			"`tabAccounting Journal Rule`.condition",
		],
	)

	for condition in [rule for rule in applicable_rules if rule.condition]:
		if frappe.safe_eval(
			condition.condition,
			None,
			{"doc": doc},
		):
			return condition.name

	if [rule for rule in applicable_rules if not rule.condition]:
		return [rule for rule in applicable_rules if not rule.condition][0].name

	return None
