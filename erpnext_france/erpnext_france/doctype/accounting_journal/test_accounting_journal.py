# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt


import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate

from erpnext.accounts.doctype.accounting_journal.accounting_journal import (
	accounting_journal_adjustment,
)
from erpnext.accounts.doctype.payment_entry.test_payment_entry import get_payment_entry

test_records = frappe.get_test_records("Sales Invoice")


class TestAccountingJournal(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		frappe.get_doc(
			{
				"doctype": "Accounting Journal",
				"journal_code": "BQ",
				"journal_name": "Banque",
				"type": "Bank",
				"account": "_Test Bank - _TC",
				"company": "_Test Company",
				"conditions": [
					{"document_type": "Payment Entry"},
				],
			}
		).insert(ignore_if_duplicate=True)

		frappe.get_doc(
			{
				"doctype": "Accounting Journal",
				"journal_code": "MD",
				"journal_name": "Miscellaneous Operations",
				"type": "Miscellaneous",
				"company": "_Test Company",
			}
		).insert(ignore_if_duplicate=True)

	def make(self):
		si = frappe.copy_doc(test_records[0])
		si.is_pos = 0
		si.insert()
		si.submit()
		return si

	def test_payment_entry_journal_adjustment(self):
		sales_invoice = self.make()

		pe = get_payment_entry("Sales Invoice", sales_invoice.name, bank_account="_Test Bank - _TC")
		pe.reference_no = "1"
		pe.reference_date = nowdate()
		pe.paid_from_account_currency = sales_invoice.currency
		pe.paid_to_account_currency = sales_invoice.currency
		pe.source_exchange_rate = 1
		pe.target_exchange_rate = 1
		pe.paid_amount = sales_invoice.outstanding_amount
		pe.insert()
		pe.submit()

		si_status = frappe.db.get_value("Sales Invoice", sales_invoice.name, "status")
		self.assertEqual(si_status, "Paid")

		pe_gl_entries = frappe.get_all(
			"GL Entry",
			filters={"voucher_type": "Payment Entry", "voucher_no": pe.name},
			fields=["name", "accounting_journal"],
		)
		accounting_journal = list(set(gl.accounting_journal for gl in pe_gl_entries))[0]
		self.assertEqual(accounting_journal, "BQ")

		accounting_journal_adjustment("Payment Entry", [pe.name], "MD")

		pe_gl_entries = frappe.get_all(
			"GL Entry",
			filters={"voucher_type": "Payment Entry", "voucher_no": pe.name, "is_cancelled": 0},
			fields=["name", "accounting_journal"],
		)
		accounting_journal = list(set(gl.accounting_journal for gl in pe_gl_entries))[0]
		self.assertEqual(accounting_journal, "MD")

		si_status = frappe.db.get_value("Sales Invoice", sales_invoice.name, "status")
		self.assertEqual(si_status, "Paid")
