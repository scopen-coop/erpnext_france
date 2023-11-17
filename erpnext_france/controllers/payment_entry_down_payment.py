import frappe
from frappe import _
from frappe.utils import  cint

def validate(doc, method):
    check_if_down_payment(doc)
    

def check_if_down_payment(doc):
    is_down_payment = False
    for d in doc.get("references"):
        if d.reference_doctype == "Sales Invoice":
            is_dp_invoice = frappe.db.get_value(
                d.reference_doctype, d.reference_name, "is_down_payment_invoice"
            )
            if cint(is_dp_invoice):
                is_down_payment = True

    doc.down_payment = is_down_payment