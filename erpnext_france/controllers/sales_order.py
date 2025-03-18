import erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice

@frappe.whitelist()
def make_sales_invoice_with_payment_terms(source_name, target_doc=None, ignore_permissions=False):
	doclist = make_sales_invoice(source_name, target_doc, ignore_permissions)



	return doclist
