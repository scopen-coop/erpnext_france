# Copyright (c) 2019, Dokos SAS and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SepaDirectDebitSettings(Document):
	def validate(self):
		if self.bank_account:
			iban, swift_number = frappe.db.get_value(
				"Bank Account", self.bank_account, ["iban", "swift_number"]
			)

			if not iban:
				frappe.throw(_("Please register an IBAN in the company's bank account"))

			if not swift_number:
				frappe.throw(_("Please register a SWIFT Number in the company's bank account"))
