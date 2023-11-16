# Copyright (c) 2019, Dokos SAS and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SepaMandate(Document):
	def validate(self):
		if not self.registered_on_gocardless and not (self.creation_date and self.bank_account):
			frappe.throw(_("Please register the creation date and a customer bank account"))

		if self.bank_account:
			party_type, party, iban, swift_number = frappe.db.get_value(
				"Bank Account", self.bank_account, ["party_type", "party", "iban", "swift_number"]
			)

			if party_type and party:
				if party_type != "Customer":
					frappe.throw(_("Please select a bank account linked to a customer"))

				if party != self.customer:
					frappe.throw(_("Please select a bank account linked to customer {0}").format(self.customer))

			if not iban:
				frappe.throw(_("Please register an IBAN in the customer's bank account"))

			if not swift_number:
				frappe.throw(_("Please register a SWIFT Number in the customer's bank account"))
