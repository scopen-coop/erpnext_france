# Copyright (c) 2021, Dokos SAS and contributors
# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import datetime
from collections import defaultdict

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, date_diff, flt, format_date, getdate, month_diff, nowdate

from erpnext_france.regional.france.general_ledger import (
	check_freezing_date,
	get_accounting_journal,
	make_entry,
	make_reverse_gl_entries,
	validate_accounting_period,
)


from erpnext.accounts.utils import get_fiscal_years

ENTRYTYPES = {"Deferred charges": "Purchase Invoice", "Deferred income": "Sales Invoice"}

ACCOUNTTYPE = {"Purchase Invoice": "expense_account", "Sales Invoice": "income_account"}


class AdjustmentEntry(Document):
	def on_submit(self):
		self._make_gl_entries()
		self.set_status()

	def on_cancel(self):
		self.ignore_linked_doctypes = "GL Entry"
		make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
		self.set_status()

	def set_status(self, status=None):
		if self.docstatus == 0:
			status = "Draft"
		elif self.docstatus == 1:
			status = "Submitted" if not status else status
		elif self.docstatus == 2:
			status = "Cancelled"

		if self.status != status:
			self.db_set("status", status)

	def reverse_gl_entries(self, date=None):
		gl_entries = frappe.get_all(
			"GL Entry",
			fields=["*"],
			filters={"voucher_type": self.doctype, "voucher_no": self.name, "is_cancelled": 0},
		)

		if gl_entries:
			validate_accounting_period(gl_entries)
			check_freezing_date(gl_entries[0]["posting_date"], False)

			for entry in gl_entries:
				name = entry["name"]
				entry["name"] = None
				if date:
					entry["posting_date"] = date
				debit = entry.get("debit", 0)
				credit = entry.get("credit", 0)

				debit_in_account_currency = entry.get("debit_in_account_currency", 0)
				credit_in_account_currency = entry.get("credit_in_account_currency", 0)

				entry["debit"] = credit
				entry["credit"] = debit
				entry["debit_in_account_currency"] = credit_in_account_currency
				entry["credit_in_account_currency"] = debit_in_account_currency
				entry["against"] = name

				if not entry.get("accounting_journal"):
					get_accounting_journal(entry)

				if entry["debit"] or entry["credit"]:
					make_entry(entry, False, "False")

	def _make_gl_entries(self):
		from erpnext.accounts.general_ledger import make_gl_entries

		if self.total_posting_amount == 0:
			return

		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)
		if len(fiscal_years) > 1:
			frappe.throw(
				_("Multiple fiscal years exist for the date {0}. Please set company in Fiscal Year").format(
					format_date(self.posting_date)
				)
			)

		fiscal_year = fiscal_years[0][0]

		gl_entries = []
		for d in self.details:
			debit_or_credit = d.debit - d.credit
			gl_entries.append(
				frappe._dict(
					{
						"company": self.company,
						"fiscal_year": fiscal_year,
						"account": d.account,
						"against": d.document_name,
						"credit": d.posting_amount if debit_or_credit >= 0 else 0.0,
						"debit": d.posting_amount if debit_or_credit <= 0 else 0.0,
						"against_voucher_type": d.document_type,
						"against_voucher": d.document_name,
						"posting_date": self.posting_date,
						"voucher_type": self.doctype,
						"voucher_no": self.name,
						"cost_center": d.cost_center,
						"accounting_journal": self.accounting_journal,
					}
				)
			)

			gl_entries.append(
				frappe._dict(
					{
						"company": self.company,
						"fiscal_year": fiscal_year,
						"account": self.adjustment_account,
						"against": d.document_name,
						"credit": d.posting_amount if debit_or_credit <= 0 else 0.0,
						"debit": d.posting_amount if debit_or_credit >= 0 else 0.0,
						"against_voucher_type": d.document_type,
						"against_voucher": d.document_name,
						"posting_date": self.posting_date,
						"voucher_type": self.doctype,
						"voucher_no": self.name,
						"cost_center": d.cost_center,
						"accounting_journal": self.accounting_journal,
					}
				)
			)

		if gl_entries:
			try:
				make_gl_entries(
					gl_entries, cancel=(self.docstatus == 2), merge_entries=True, update_outstanding="False"
				)
				frappe.db.commit()
			except Exception:
				frappe.db.rollback()
				traceback = frappe.get_traceback()
				frappe.throw(traceback)


@frappe.whitelist()
def get_documents(entry_type, date, company):
	doctype = ENTRYTYPES.get(entry_type)

	if not doctype:
		return []

	account_type = ACCOUNTTYPE.get(doctype)

	documents = frappe.db.sql(
		f"""
		SELECT dt.name as document_name, dt.from_date, dt.to_date,
		'{doctype}' as document_type,
		it.{account_type} as account, it.cost_center
		FROM `tab{doctype}` as dt
		LEFT JOIN `tab{doctype} Item` as it
		ON it.parent = dt.name
		WHERE dt.company={frappe.db.escape(company)}
		AND dt.from_date <= {frappe.db.escape(date)}
		AND dt.to_date > {frappe.db.escape(date)}
		AND dt.docstatus = 1
	""",
		as_dict=True,
	)

	if not documents:
		return []

	documents = [frappe._dict(line) for line in {tuple(document.items()) for document in documents}]

	documents_list = ", ".join([f"{frappe.db.escape(x.document_name)}" for x in documents])
	account_list = ", ".join([f"{frappe.db.escape(x.account)}" for x in documents])

	gl_entries = frappe.db.sql(
		f"""
		SELECT account, debit, credit, voucher_type, voucher_no
		FROM `tabGL Entry`
		WHERE voucher_type='{doctype}'
		AND voucher_no in ({documents_list})
		AND account in ({account_list})
	""",
		as_dict=True,
	)

	gl_by_document = {gl_entry.voucher_no: defaultdict(list) for gl_entry in gl_entries}
	for gl_entry in gl_entries:
		if gl_entry.account in gl_by_document[gl_entry.voucher_no]:
			gl_by_document[gl_entry.voucher_no][gl_entry.account][0] += gl_entry.debit
			gl_by_document[gl_entry.voucher_no][gl_entry.account][1] += gl_entry.credit
		else:
			gl_by_document[gl_entry.voucher_no][gl_entry.account] = [gl_entry.debit, gl_entry.credit]

	total_credit = 0.0
	total_debit = 0.0
	total_posting_amount = 0.0
	for document in documents:
		debit = gl_by_document.get(document.document_name, {}).get(document.account, [0.0, 0.0])[0]
		total_debit += debit

		credit = gl_by_document.get(document.document_name, {}).get(document.account, [0.0, 0.0])[1]
		total_credit += credit

		net_amount = abs(debit - credit)
		posting_amount = get_posting_amount(document.to_date, date, net_amount)
		total_posting_amount += posting_amount

		document.update({"debit": debit, "credit": credit, "posting_amount": posting_amount})

	return {
		"documents": documents,
		"total_debit": total_debit,
		"total_credit": total_credit,
		"total_posting_amount": total_posting_amount,
	}


def get_posting_amount(to_date, date, net_amount):
	no_of_days = 0.0
	no_of_months = month_diff(to_date, add_days(date, 1))

	for month in range(no_of_months):
		if month + 1 == no_of_months:
			no_of_days += min(
				date_diff(to_date, datetime.date(getdate(to_date).year, getdate(to_date).month, 1)), 30
			)
		else:
			no_of_days += 30

	if no_of_days:
		posting_amount = flt(net_amount) * (flt(no_of_days) / 360)
		return posting_amount if posting_amount > 0.1 else 0.0
	else:
		return 0.0


def reverse_adjustment_entries():
	for entry in frappe.get_all(
		"Adjustment Entry",
		filters={"status": "Submitted", "docstatus": 1, "reversal_date": ("<=", nowdate())},
		fields=["name", "reversal_date"],
	):
		doc = frappe.get_doc("Adjustment Entry", entry.name)
		doc.reverse_gl_entries(entry.reversal_date)
		doc.set_status("Reversed")
