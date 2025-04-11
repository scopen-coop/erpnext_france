import frappe

def before_save(doc, method):
	if not 0 < len(doc.suppliers) < 2 :
		doc.before_save()
		return

	update_supplier_part_no(doc, doc.suppliers[0].supplier)


def update_supplier_part_no(doc, supplier):
	for item in doc.items:
		supplier_part_no = frappe.db.get_value(
			"Item Supplier", {"parent": item.item_code, "supplier": supplier}, "supplier_part_no"
		)

		if supplier_part_no:
			item.supplier_part_no = supplier_part_no
