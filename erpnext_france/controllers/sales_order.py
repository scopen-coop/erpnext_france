import frappe
from frappe import _
from frappe.utils import getdate
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice


@frappe.whitelist()
def make_sales_invoice_with_payment_terms(source_name, target_doc=None, ignore_permissions=False):
	doclist = make_sales_invoice(source_name, target_doc, ignore_permissions)

	customer = frappe.get_doc('Customer', doclist.get("customer"))
	doclist.payment_terms_template = customer.get('payment_terms')
	return doclist


def verify_sales_orders_terms(doc, method):
	old_doc = doc.get_doc_before_save()
	if not old_doc:
		return

	payments_entry_reference = frappe.get_all(
		'Payment Entry Reference',
		['parent', 'payment_term'],
		{
			'reference_doctype': 'Sales Order',
			'reference_name': old_doc.name
		}
	)

	payments_parent_name = [payment_entry_reference.parent for payment_entry_reference in payments_entry_reference]

	payments_entry = frappe.get_list(
		'Payment Entry',
		['name'],
		{
			'name': ['in', payments_parent_name],
			'docstatus': 1
		}
	)

	payments_entry_name = [payment_entry.name for payment_entry in payments_entry]
	payments_list = [
		payment_entry_reference.payment_term
		for payment_entry_reference in payments_entry_reference
		if payment_entry_reference.parent in payments_entry_name
	]

	for term in old_doc.payment_schedule:
		if term.payment_term not in payments_list:
			continue

		new_terms = [new_term for new_term in doc.payment_schedule if term.name == new_term.name]

		if len(new_terms) <= 0:
			frappe.throw(_('Cannot Delete term {0} because its on a payment'.format(term.payment_term)))

		new_term = new_terms[0]
		if (
				new_term.payment_term != term.payment_term
				or new_term.description != term.description
				or getdate(new_term.due_date) != getdate(term.due_date)
				or new_term.base_payment_amount != term.base_payment_amount
		):
			frappe.throw(_('Cannot Modify term {0} because its on a payment'.format(term.payment_term)))
