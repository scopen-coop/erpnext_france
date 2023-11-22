import frappe
from frappe import _
from erpnext_france.controllers.party import get_party_account
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.utils import (cint, flt)

def validate(doc, method):
	if cint(doc.is_down_payment_invoice) and len([x.sales_order for x in doc.get("items")]) > 1:
		frappe.throw(_("Down payment invoices can only be made against a single sales order."))

	validate_down_payment_advances(doc)
	set_income_account_for_down_payments(doc)

def validate_down_payment_advances(doc):
	for advance in doc.get("advances"):
		if (
		flt(advance.allocated_amount) <= flt(advance.advance_amount)
		and advance.reference_type == "Payment Entry"
		and cint(advance.is_down_payment)
		):
			advance.allocated_amount = advance.advance_amount
	


def set_income_account_for_down_payments(doc):
	if doc.is_down_payment_invoice:
		debit_to = get_party_account(
			"Customer",
			doc.customer,
			doc.company,
			doc.is_down_payment_invoice
		)

		if isinstance(debit_to, list):
			debit_to = debit_to[-1]

		for d in doc.get("items"):
			d.income_account = debit_to
