import frappe
from frappe import _


@frappe.whitelist()
def payment_entry_ref(reference_doctype, reference_name):
	payments = frappe.get_all(
		"Payment Entry Reference",
		fields=["parent", "payment_term", "allocated_amount"],
		filters={
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
		},
	)

	return payments
