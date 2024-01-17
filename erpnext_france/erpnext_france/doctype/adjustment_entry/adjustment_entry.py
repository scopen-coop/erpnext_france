# Copyright (c) 2021, Dokos SAS and contributors
# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import datetime
from collections import defaultdict

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, date_diff, flt, format_date, getdate, month_diff, nowdate

from erpnext.accounts.general_ledger import (
	check_freezing_date,
	make_entry,
	make_reverse_gl_entries,
	validate_accounting_period,
)

from erpnext_france.utils.accounting_entry_number import get_accounting_number

from erpnext.accounts.utils import get_fiscal_year

ENTRYTYPES = {"Deferred charges": "Purchase Invoice", "Deferred income": "Sales Invoice"}

ACCOUNTTYPE = {"Purchase Invoice": "expense_account", "Sales Invoice": "income_account"}


class AdjustmentEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from erpnext.accounts.doctype.adjustment_entry_detail.adjustment_entry_detail import (
			AdjustmentEntryDetail,
		)

		accounting_journal: DF.Link | None
		adjustment_account: DF.Link
		amended_from: DF.Link | None
		auto_repeat: DF.Link | None
		company: DF.Link
		details: DF.Table[AdjustmentEntryDetail]
		entry_type: DF.Literal["Deferred charges", "Deferred income"]
		error: DF.SmallText | None
		naming_series: DF.Literal["ACC-ADJ-.YYYY.-"]
		posting_date: DF.Date
		reversal_date: DF.Date
		status: DF.Literal["Draft", "Submitted", "Reversed", "Cancelled", "Error"]
		title: DF.Data | None
		total_credit: DF.Currency
		total_debit: DF.Currency
		total_posting_amount: DF.Currency
	# end: auto-generated types

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
			new_fiscal_year = get_fiscal_year(date, company=self.company)

			if not new_fiscal_year:
				self.db_set("status", "Error")
				error_msg = _("No fiscal year could be found to reverse this entry")
				self.db_set("error", error_msg)
				frappe.throw(error_msg)

			self.db_set("error", "")
			fiscal_year = new_fiscal_year[0]
			accounting_number = get_accounting_number(gl_entries[0])

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
				entry["accounting_entry_number"] = accounting_number
				entry["fiscal_year"] = fiscal_year


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

	dt = frappe.qb.DocType(doctype)
	dti = frappe.qb.DocType(doctype + " Item")
	documents = (
		frappe.qb.from_(dt)
		.left_join(dti)
		.on(dti.parent == dt.name)
		.select(dt.name, dti[account_type], dti.cost_center)
		.where((dt.company == company) & (dt.docstatus == 1))
		.run(as_dict=True)
	)

	if not documents:
		return []

	frappe.throw(str(frappe.qb.from_(dt)
		.left_join(dti)
		.on(dti.parent == dt.name)
		.select(dt.name, dti[account_type], dti.cost_center)
		.where((dt.company == company) & (dt.docstatus == 1))))
	documents_list = list(set([x.name for x in documents]))
	account_list = list(set([x[account_type] for x in documents]))
	fiscal_year = get_fiscal_year(date=date, company=company)

	gle = frappe.qb.DocType('GL Entry')
	gl_entries = (
		frappe.qb.from_(gle)
		.select(gle.account, gle.debit, gle.credit, gle.voucher_type, gle.voucher_no)
		.where(gle.voucher_type == doctype)
		.where(gle.voucher_no.isin(documents_list))
		.where(gle.account.isin(account_list))
		.where(gle.fiscal_year == fiscal_year[0])
		.run(as_dict=True)
	)

	gl_by_document = {x:{y: [0,0] for y in account_list} for x in documents_list}

	for gl_entry in gl_entries:
		if gl_entry.account in gl_by_document[gl_entry.voucher_no]:
			gl_by_document[gl_entry.voucher_no][gl_entry.account][0] += gl_entry.debit
			gl_by_document[gl_entry.voucher_no][gl_entry.account][1] += gl_entry.credit
		else:
			gl_by_document[gl_entry.voucher_no][gl_entry.account] = [gl_entry.debit, gl_entry.credit]

	total_credit = 0.0
	total_debit = 0.0
	total_posting_amount = 0.0

	documents_array = []
	for document in documents:
		debit = gl_by_document[document.name][document[account_type]][0]
		total_debit += debit

		credit = gl_by_document[document.name][document[account_type]][1]
		total_credit += credit

		if not debit and not credit:
			documents.remove(document)
			continue

		posting_amount = abs(debit - credit)
		total_posting_amount += posting_amount

		documents_array.append({
			"debit": debit,
			"credit": credit,
			"posting_amount": posting_amount,
			"account": document[account_type],
			"document_name": document.name,
			"document_type": doctype,
			"cost_center": document.cost_center
		})

	return {
		"documents": documents_array,
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
