# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def validate(doc, method):
	set_advance_for_down_payment_entries(doc)
	

def set_advance_for_down_payment_entries(doc):
	for account in doc.accounts:
		is_down_payment_invoice = frappe.db.get_value("Sales Invoice", account.reference_name, "is_down_payment_invoice")
		if account.reference_type == "Sales Invoice" and is_down_payment_invoice:
			account.is_advance = "Yes"