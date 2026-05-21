import frappe


def execute():
	frappe.reload_doc("Accounts", "doctype", "Payment Term")
	payment_terms = frappe.get_all("Payment Term")
	for payment_term in payment_terms:
		if payment_term.get("custom_due_date_based_on_france") is None and payment_term.get(
			"due_date_based_on"
		):
			payment_term.custom_due_date_based_on_france = payment_term.due_date_based_on
			payment_term.save()
