# Copyright (c) 2025, Scopen and Contributors
# See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SEPAMandate(Document):
	def validate(self):
		self.validate_unique_active_mandate()
		self.validate_bank_account()

	def validate_unique_active_mandate(self):
		"""Ensure only one active mandate per customer and bank account (IBAN)"""
		if self.status == "Active":
			# Get the IBAN from the linked bank account
			bank_account = frappe.get_doc("Bank Account", self.bank_account)

			existing = frappe.db.exists(
				"SEPA Mandate",
				{
					"customer": self.customer,
					"bank_account": self.bank_account,
					"status": "Active",
					"name": ["!=", self.name]
				}
			)

			if existing:
				frappe.throw(
					_("An active SEPA Mandate already exists for this customer and bank account. Please cancel the existing mandate before activating a new one.")
				)

	def validate_bank_account(self):
		"""Validate that the bank account belongs to the customer"""
		if self.bank_account and self.customer:
			bank_account = frappe.get_doc("Bank Account", self.bank_account)

			# Check if the bank account is linked to the customer
			if bank_account.party_type != "Customer" or bank_account.party != self.customer:
				frappe.throw(
					_("The selected bank account does not belong to the customer {0}").format(self.customer)
				)

	def on_update(self):
		"""Sync active mandate to customer record"""
		if self.status == "Active":
			frappe.db.set_value("Customer", self.customer, "sepa_mandate", self.name)
		elif self.status == "Cancelled":
			current = frappe.db.get_value("Customer", self.customer, "sepa_mandate")
			if current == self.name:
				frappe.db.set_value("Customer", self.customer, "sepa_mandate", None)

	@frappe.whitelist()
	def update_to_recurring(self):
		"""Update sequence type from FRST to RCUR after first successful debit"""
		if self.sequence_type == "FRST" and self.status == "Active":
			self.sequence_type = "RCUR"
			self.save()
			frappe.msgprint(_("Mandate updated to recurring (RCUR) after first successful debit"))
