# Copyright (c) 2019, Dokos SAS and contributors
# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.email.doctype.notification.notification import get_context
from frappe.model.document import Document
import copy

from erpnext_france.regional.france.general_ledger import get_accounting_number
from erpnext.accounts.general_ledger import (
	make_entry,
	check_freezing_date,
	set_as_cancel,
	validate_accounting_period,
)

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

		make_reverse_gl_entries_without_cancelling(voucher_type=doctype, voucher_no=docname)

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

def make_reverse_gl_entries_without_cancelling(
	voucher_type=None,
	voucher_no=None,
):
	"""
	Get original gl entries of the voucher
	and make reverse gl entries by swapping debit and credit
	"""

	gl_entry = frappe.qb.DocType("GL Entry")
	gl_entries = (
		frappe.qb.from_(gl_entry)
		.select("*")
		.where(gl_entry.voucher_type == voucher_type)
		.where(gl_entry.voucher_no == voucher_no)
		.where(gl_entry.is_cancelled == 0)
		.for_update()
	).run(as_dict=1)

	if not gl_entries:
		return

	validate_accounting_period(gl_entries)
	check_freezing_date(gl_entries[0]["posting_date"], False)
	set_as_cancel(gl_entries[0]["voucher_type"], gl_entries[0]["voucher_no"])

	accounting_number = get_accounting_number(gl_entries[0])
	for entry in gl_entries:
		new_gle = copy.deepcopy(entry)
		new_gle["name"] = None
		new_gle["accounting_entry_number"] = accounting_number
		debit = new_gle.get("debit", 0)
		credit = new_gle.get("credit", 0)

		debit_in_account_currency = new_gle.get("debit_in_account_currency", 0)
		credit_in_account_currency = new_gle.get("credit_in_account_currency", 0)

		new_gle["debit"] = credit
		new_gle["credit"] = debit
		new_gle["debit_in_account_currency"] = credit_in_account_currency
		new_gle["credit_in_account_currency"] = debit_in_account_currency

		if not new_gle["remarks"]:
			new_gle["remarks"] = _("On cancellation of ") + new_gle["voucher_no"]

		new_gle["is_cancelled"] = 1

		if not new_gle.get("accounting_journal"):
			get_accounting_journal(new_gle)

		if new_gle["debit"] or new_gle["credit"]:
			make_entry(new_gle, False, "Yes")
