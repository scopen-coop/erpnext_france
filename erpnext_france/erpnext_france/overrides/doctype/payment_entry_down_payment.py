# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _
from frappe.utils import  cint, flt
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry
from erpnext_france.controllers.accounts_controller import set_total_advance_paid


class PaymentEntryDownPayment(PaymentEntry):
	def validate(self):
		super(PaymentEntryDownPayment, self).validate()
		
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
		if self.party_account:
			if self.payment_type == "Receive":
				against_account = self.paid_to
			else:
				against_account = self.paid_from

			party_gl_dict = self.get_gl_dict(
				{
					"account": self.party_account,
					"party_type": self.party_type,
					"party": self.party,
					"against": against_account,
					"account_currency": self.party_account_currency,
					"cost_center": self.cost_center,
					"accounting_journal": self.accounting_journal,	# Erpnext France
				},
				item=self,
			)

			dr_or_cr = (
				"credit" if erpnext.get_party_account_type(self.party_type) == "Receivable" else "debit"
			)

			for d in self.get("references"):
				cost_center = self.cost_center
				if d.reference_doctype == "Sales Invoice" and not cost_center:
					cost_center = frappe.db.get_value(d.reference_doctype, d.reference_name, "cost_center")
				gle = party_gl_dict.copy()
				gle.update(
					{
						"against_voucher_type": d.reference_doctype,
						"against_voucher": d.reference_name,
						"cost_center": cost_center,
					}
				)

				allocated_amount_in_company_currency = self.calculate_base_allocated_amount_for_reference(d)

				gle.update(
					{
						dr_or_cr + "_in_account_currency": d.allocated_amount,
						dr_or_cr: allocated_amount_in_company_currency,
					}
				)

				gl_entries.append(gle)

			if self.unallocated_amount:
				exchange_rate = self.get_exchange_rate()
				base_unallocated_amount = self.unallocated_amount * exchange_rate

				gle = party_gl_dict.copy()

				gle.update(
					{
						dr_or_cr + "_in_account_currency": self.unallocated_amount,
						dr_or_cr: base_unallocated_amount,
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
						"credit": self.base_paid_amount,
						"cost_center": self.cost_center,
						"accounting_journal": self.accounting_journal,	# Erpnext France
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
						"debit": self.base_received_amount,
						"cost_center": self.cost_center,
						"accounting_journal": self.accounting_journal,	# Erpnext France
					},
					item=self,
				)
			)

		if self.payment_type == "Internal Transfer":
			inter_banks_transfer_account = frappe.get_cached_value(
				"Company", self.company, "inter_banks_transfer_account"
			)
			if inter_banks_transfer_account:
				gl_entries.append(
					self.get_gl_dict(
						{
							"account": inter_banks_transfer_account,
							"account_currency": self.paid_from_account_currency,
							"against": self.paid_from,
							"debit_in_account_currency": self.paid_amount,
							"debit": self.base_paid_amount,
							"cost_center": self.cost_center,
							"accounting_journal": self.accounting_journal,	# Erpnext France
						},
						item=self,
					)
				)

				gl_entries.append(
					self.get_gl_dict(
						{
							"account": inter_banks_transfer_account,
							"account_currency": self.paid_to_account_currency,
							"against": self.paid_to,
							"credit_in_account_currency": self.paid_amount,
							"credit": self.base_paid_amount,
							"cost_center": self.cost_center,
							"accounting_journal": self.accounting_journal,	# Erpnext France
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
						"cost_center": d.cost_center,
						"post_net_value": True,
						"accounting_journal": self.accounting_journal,	# Erpnext France
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
							"cost_center": self.cost_center,
							"post_net_value": True,
							"accounting_journal": self.accounting_journal,	# Erpnext France
						},
						account_currency,
						item=d,
					)
				)

	def add_deductions_gl_entries(self, gl_entries):
		for d in self.get("deductions"):
			if d.amount:
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
							"debit": d.amount,
							"cost_center": d.cost_center,
							"accounting_journal": self.accounting_journal,	# Erpnext France
						},
						item=d,
					)
				)

	def get_cash_flow_journal(self, account):  # Erpnext France
		rules = frappe.get_all(
			"Accounting Journal",
			filters={"company": self.company, "disabled": 0},
			fields=[
				"name",
				"type",
				"account",
				"`tabAccounting Journal Rule`.document_type",
				"`tabAccounting Journal Rule`.condition",
			],
		)

		applicable_rules = [
			rule for rule in rules if (rule.document_type == self.doctype and rule.account == account)
		]

		for condition in [rule for rule in applicable_rules if rule.condition]:
			if frappe.safe_eval(condition.condition, None, {"doc": self.as_dict()}):
				return condition.name

		if [rule for rule in applicable_rules if not rule.condition]:
			return [rule for rule in applicable_rules if not rule.condition][0].name

	def update_advance_paid(self):
		if self.payment_type in ("Receive", "Pay") and self.party:
			for d in self.get("references"):
				if d.allocated_amount and d.reference_doctype in frappe.get_hooks("advance_payment_doctypes"):
					doc = frappe.get_doc(
						d.reference_doctype, d.reference_name, for_update=True
					)
					set_total_advance_paid(doc)

				if d.allocated_amount and d.reference_doctype == "Sales Invoice": # Erpnext France
					so = frappe.db.get_value(
						"Sales Invoice Item",
						{"parenttype": "Sales Invoice", "parent": d.reference_name},
						"sales_order",
					)
					if so:
						doc = frappe.get_doc("Sales Order", so, for_update=True)

						set_total_advance_paid(doc)
