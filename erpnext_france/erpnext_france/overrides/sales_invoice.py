import frappe
from frappe import _


def validate(doc, method):
	"""Hook for Sales Invoice validation"""
	# Pre-fill default mode of payment from customer
	if doc.customer and not doc.get("__islocal"):
		customer = frappe.get_doc("Customer", doc.customer)
		if customer.get("default_mode_of_payment") and not doc.get("mode_of_payment"):
			# Map to actual mode of payment
			mode_mapping = {
				"Direct Debit": "SEPA Direct Debit",
				"Credit Transfer": "SEPA Credit Transfer"
			}
			mapped_mode = mode_mapping.get(customer.default_mode_of_payment)
			if mapped_mode and frappe.db.exists("Mode of Payment", mapped_mode):
				doc.mode_of_payment = mapped_mode
