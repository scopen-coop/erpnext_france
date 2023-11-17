import frappe
from frappe import _


def validate(doc, method):
    set_advance_for_down_payment_entries(doc)
    

def set_advance_for_down_payment_entries(doc):
    for account in doc.accounts:
        if account.reference_type == "Sales Invoice":
            frappe.throw(str(account))
            if frappe.db.get_value("Sales Invoice", account.reference_name, "is_down_payment_invoice"):
                account.is_advance = "Yes"