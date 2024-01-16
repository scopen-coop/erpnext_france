# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.naming import make_autoname
from frappe.utils import cint

def add_accounting_entry_number(gl_entry, action):
	if gl_entry.accounting_entry_number:
		return

	linked_gl_entries = frappe.get_all(
		'GL Entry',
		fields={"name", "accounting_entry_number"},
		filters={"voucher_no": gl_entry.voucher_no}
	)

	accounting_entry_number = ''
	for linked_gl_entry in linked_gl_entries:
		if linked_gl_entry.name == gl_entry.name:
			continue

		if linked_gl_entry.accounting_entry_number:
			accounting_entry_number = linked_gl_entry.accounting_entry_number

	if not accounting_entry_number:
		accounting_entry_number = make_autoname(_("AEN-.fiscal_year.-.#########"), "GL Entry", gl_entry)

	gl_entry.accounting_entry_number = accounting_entry_number
	gl_entry.accounting_journal = get_accounting_journal(gl_entry)

	gl_entry.save()

def get_accounting_journal(entry):
	rules = frappe.get_all(
		"Accounting Journal",
		filters={"company": entry.company, "disabled": 0},
		fields=[
			"name",
			"type",
			"account",
			"`tabAccounting Journal Rule`.document_type",
			"`tabAccounting Journal Rule`.condition",
		],
	)

	applicable_rules = [
		rule for rule in rules if (rule.account in (entry.account, entry.against, None))
	]

	if applicable_rules:
		applicable_rules = sorted(
			[rule for rule in applicable_rules if rule.document_type in (entry.voucher_type, None)],
			key=lambda r: r.get("document_type") or "",
			reverse=True,
		)
	else:
		applicable_rules = [rule for rule in rules if rule.document_type == entry.voucher_type]

	accounting_journal = ''
	for condition in [rule for rule in applicable_rules if rule.condition]:
		if frappe.safe_eval(
				condition.condition,
				None,
				{"doc": frappe.get_doc(entry.voucher_type, entry.voucher_no).as_dict()},
		):
			accounting_journal = condition.name
			break

	if not accounting_journal and [
		rule for rule in applicable_rules if not rule.condition
	]:
		accounting_journal = [rule for rule in applicable_rules if not rule.condition][0].name

	if not accounting_journal:
		accounting_journal = frappe.db.get_value(
			"GL Entry",
			dict(accounting_entry_number=entry.accounting_entry_number),
			"accounting_journal",
		)

	if not accounting_journal and cint(
			frappe.db.get_single_value("Accounts Settings", "mandatory_accounting_journal")
	):
		frappe.throw(
			_(
				"Please configure an accounting journal for this transaction type and account: {0} - {1}"
			).format(_(entry.voucher_type), entry.account)
		)

	return accounting_journal

