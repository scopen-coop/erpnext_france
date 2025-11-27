# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import erpnext
import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry
from erpnext.accounts.utils import get_account_currency
from frappe import _
from frappe.utils import cint, flt

from erpnext_france.controllers.accounts_controller import set_total_advance_paid


class PaymentEntryDownPayment(PaymentEntry):
	def validate(self):
		super().validate()
		# self.set_advance_reference_for_down_payments() # DOKOS
		self.check_if_down_payment()
		self.update_unreconciled_amount()

	def check_if_down_payment(self):
		is_down_payment = False
		for d in self.get("references"):
			if d.reference_doctype == "Sales Invoice":
				is_dp_invoice = frappe.db.get_value(
					d.reference_doctype, d.reference_name, "is_down_payment_invoice"
				)
				if cint(is_dp_invoice):
					is_down_payment = True
		self.down_payment = is_down_payment

	def update_unreconciled_amount(self):
		self.unreconciled_from_amount = (
			self.paid_amount if self.payment_type in ("Pay", "Internal Transfer") else 0.0
		)
		self.unreconciled_to_amount = (
			self.paid_amount if self.payment_type in ("Receive", "Internal Transfer") else 0.0
		)
		self.unreconciled_amount = flt(self.unreconciled_from_amount) + flt(self.unreconciled_to_amount)

	def add_party_gl_entries(self, gl_entries):
		if not self.party_account:
			return

		advance_payment_doctypes = self.get_advance_payment_doctypes()
		if self.payment_type == "Receive":
			against_account = self.paid_to
		else:
			against_account = self.paid_from

		party_account_type = frappe.db.get_value("Party Type", self.party_type, "account_type")

		party_gl_dict = self.get_gl_dict(
			{
				"account": self.party_account,
				"party_type": self.party_type,
				"party": self.party,
				"against": against_account,
				"account_currency": self.party_account_currency,
				"cost_center": self.cost_center,
				"accounting_journal": self.accounting_journal,
			},
			item=self,
		)

		for d in self.get("references"):
			# re-defining dr_or_cr for every reference in order to avoid the last value affecting calculation of reverse
			dr_or_cr = "credit" if self.payment_type == "Receive" else "debit"
			cost_center = self.cost_center
			if d.reference_doctype == "Sales Invoice" and not cost_center:
				cost_center = frappe.db.get_value(d.reference_doctype, d.reference_name, "cost_center")

			gle = party_gl_dict.copy()

			allocated_amount_in_company_currency = self.calculate_base_allocated_amount_for_reference(d)

			if (
				d.reference_doctype in ["Sales Invoice", "Purchase Invoice"]
				and d.allocated_amount < 0
				and (
					(party_account_type == "Receivable" and self.payment_type == "Pay")
					or (party_account_type == "Payable" and self.payment_type == "Receive")
				)
			):
				# reversing dr_cr because it will get reversed in gl processing due to negative amount
				dr_or_cr = "debit" if dr_or_cr == "credit" else "credit"

			gle.update(
				self.get_gl_dict(
					{
						"account": self.party_account,
						"party_type": self.party_type,
						"party": self.party,
						"against": against_account,
						"account_currency": self.party_account_currency,
						"cost_center": cost_center,
						dr_or_cr + "_in_account_currency": d.allocated_amount,
						dr_or_cr: allocated_amount_in_company_currency,
						dr_or_cr + "_in_transaction_currency": d.allocated_amount
						if self.transaction_currency == self.party_account_currency
						else allocated_amount_in_company_currency / self.transaction_exchange_rate,
						"advance_voucher_type": d.advance_voucher_type,
						"advance_voucher_no": d.advance_voucher_no,
						"transaction_exchange_rate": self.target_exchange_rate,
					},
					item=self,
				)
			)

			if d.reference_doctype in advance_payment_doctypes:
				# advance reference
				gle.update(
					{
						"against_voucher_type": self.doctype,
						"against_voucher": self.name,
						"advance_voucher_type": d.reference_doctype,
						"advance_voucher_no": d.reference_name,
					}
				)

			elif self.get("book_advance_payments_in_separate_party_account"):  # @dokos
				# Do not reference Invoices while Advance is in separate party account
				gle.update({"against_voucher_type": self.doctype, "against_voucher": self.name})
			else:
				gle.update(
					{
						"against_voucher_type": d.reference_doctype,
						"against_voucher": d.reference_name,
					}
				)

			gl_entries.append(gle)

		if self.unallocated_amount:
			dr_or_cr = "credit" if self.payment_type == "Receive" else "debit"
			exchange_rate = self.get_exchange_rate()
			base_unallocated_amount = self.unallocated_amount * exchange_rate

			gle = party_gl_dict.copy()

			gle.update(
				self.get_gl_dict(
					{
						"account": self.party_account,
						"party_type": self.party_type,
						"party": self.party,
						"against": against_account,
						"account_currency": self.party_account_currency,
						"cost_center": self.cost_center,
						dr_or_cr + "_in_account_currency": self.unallocated_amount,
						dr_or_cr + "_in_transaction_currency": self.unallocated_amount
						if self.party_account_currency == self.transaction_currency
						else base_unallocated_amount / self.transaction_exchange_rate,
						dr_or_cr: base_unallocated_amount,
						"is_advance": "Yes",  # @dokos
					},
					item=self,
				)
			)
			if self.book_advance_payments_in_separate_party_account:
				gle.update(
					{
						"against_voucher_type": "Payment Entry",
						"against_voucher": self.name,
					}
				)
			gl_entries.append(gle)

	def add_bank_gl_entries(self, gl_entries):
		if self.payment_type in ("Pay", "Internal Transfer"):
			gl_entries.append(
				self.get_gl_dict(
					{
						"account": self.paid_from,
						"account_currency": self.paid_from_account_currency,
						"against": self.party if self.payment_type == "Pay" else self.paid_to,
						"credit_in_account_currency": self.paid_amount,
						"credit_in_transaction_currency": self.paid_amount
						if self.paid_from_account_currency == self.transaction_currency
						else self.base_paid_amount / self.transaction_exchange_rate,
						"credit": self.base_paid_amount,
						"cost_center": self.cost_center,
						"accounting_journal": self.accounting_journal,  # Erpnext France
						"post_net_value": True,
					},
					item=self,
				)
			)
		if self.payment_type in ("Receive", "Internal Transfer"):
			gl_entries.append(
				self.get_gl_dict(
					{
						"account": self.paid_to,
						"account_currency": self.paid_to_account_currency,
						"against": self.party if self.payment_type == "Receive" else self.paid_from,
						"debit_in_account_currency": self.received_amount,
						"debit_in_transaction_currency": self.received_amount
						if self.paid_to_account_currency == self.transaction_currency
						else self.base_received_amount / self.transaction_exchange_rate,
						"debit": self.base_received_amount,
						"cost_center": self.cost_center,
						"accounting_journal": self.accounting_journal,  # Erpnext France
					},
					item=self,
				)
			)

	def add_tax_gl_entries(self, gl_entries):
		for d in self.get("taxes"):
			account_currency = get_account_currency(d.account_head)
			if account_currency != self.company_currency:
				frappe.throw(_("Currency for {0} must be {1}").format(d.account_head, self.company_currency))

			if self.payment_type in ("Pay", "Internal Transfer"):
				dr_or_cr = "debit" if d.add_deduct_tax == "Add" else "credit"
				rev_dr_or_cr = "credit" if dr_or_cr == "debit" else "debit"
				against = self.party or self.paid_from
			elif self.payment_type == "Receive":
				dr_or_cr = "credit" if d.add_deduct_tax == "Add" else "debit"
				rev_dr_or_cr = "credit" if dr_or_cr == "debit" else "debit"
				against = self.party or self.paid_to

			payment_account = self.get_party_account_for_taxes()
			tax_amount = d.tax_amount
			base_tax_amount = d.base_tax_amount

			gl_entries.append(
				self.get_gl_dict(
					{
						"account": d.account_head,
						"against": against,
						dr_or_cr: tax_amount,
						dr_or_cr + "_in_account_currency": base_tax_amount
						if account_currency == self.company_currency
						else d.tax_amount,
						dr_or_cr + "_in_transaction_currency": base_tax_amount
						/ self.transaction_exchange_rate,
						"cost_center": d.cost_center,
						"post_net_value": True,
						"accounting_journal": self.accounting_journal,  # Erpnext France
					},
					account_currency,
					item=d,
				)
			)

			if not d.included_in_paid_amount:
				if get_account_currency(payment_account) != self.company_currency:
					if self.payment_type == "Receive":
						exchange_rate = self.target_exchange_rate
					elif self.payment_type in ["Pay", "Internal Transfer"]:
						exchange_rate = self.source_exchange_rate
					base_tax_amount = flt((tax_amount / exchange_rate), self.precision("paid_amount"))

				gl_entries.append(
					self.get_gl_dict(
						{
							"account": payment_account,
							"against": against,
							rev_dr_or_cr: tax_amount,
							rev_dr_or_cr + "_in_account_currency": base_tax_amount
							if account_currency == self.company_currency
							else d.tax_amount,
							rev_dr_or_cr + "_in_transaction_currency": base_tax_amount
							/ self.transaction_exchange_rate,
							"cost_center": self.cost_center,
							"post_net_value": True,
							"accounting_journal": self.accounting_journal,  # Erpnext France
						},
						account_currency,
						item=d,
					)
				)

	def add_deductions_gl_entries(self, gl_entries):
		for d in self.get("deductions"):
			if not d.amount:
				continue

			account_currency = get_account_currency(d.account)
			if account_currency != self.company_currency:
				frappe.throw(_("Currency for {0} must be {1}").format(d.account, self.company_currency))

			gl_entries.append(
				self.get_gl_dict(
					{
						"account": d.account,
						"account_currency": account_currency,
						"against": self.party or self.paid_from,
						"debit_in_account_currency": d.amount,
						"debit_in_transaction_currency": d.amount / self.transaction_exchange_rate,
						"debit": d.amount,
						"cost_center": d.cost_center,
						"accounting_journal": self.accounting_journal,  # Erpnext France
					},
					item=d,
				)
			)
