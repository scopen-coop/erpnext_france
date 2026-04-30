import frappe
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice
from frappe import _
from frappe.utils import getdate


class PurchaseInvoice(PurchaseInvoice):
	def set_payment_schedule(self):
		import erpnext.controllers.accounts_controller as ac

		from erpnext_france.controllers.party import get_payment_term_details as our_get_payment_term_details

		original = ac.get_payment_term_details
		ac.get_payment_term_details = our_get_payment_term_details
		try:
			super().set_payment_schedule()
		finally:
			ac.get_payment_term_details = original

	def validate_due_date(self):
		if self.get("is_pos"):
			return
		from erpnext_france.controllers.party import validate_due_date as validate_due_date_france

		posting_date = self.bill_date or self.posting_date
		if frappe.flags.in_import and getdate(self.due_date) < getdate(posting_date):
			self.due_date = posting_date
		else:
			validate_due_date_france(
				posting_date, self.due_date, self.bill_date, self.payment_terms_template, self.doctype
			)
