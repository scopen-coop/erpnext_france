import frappe


def before_save(doc, method):
	if not doc.buying or not doc.supplier:
		doc.before_save()
		return

	parameters = frappe.get_doc("ERPNext France Settings")

	if not parameters.update_item_supplier_part_no:
		doc.before_save()
		return

	supplier_part_no = frappe.db.get_value(
		"Item Supplier", {"parent": doc.item_code, "supplier": doc.supplier}, "supplier_part_no"
	)

	if supplier_part_no:
		doc.reference = supplier_part_no
	else:
		doc.reference = doc.supplier + " - " + doc.item_code
		update_item_supplier(doc.item_code, doc.supplier)


def update_item_supplier(item_code, supplier_name):
	item = frappe.get_doc("Item", item_code)

	supplier_item = frappe.get_doc(
		{
			"doctype": "Item Supplier",
			"parent": item_code,
			"parenttype": "Item",
			"parentfield": "supplier_items",
			"supplier": supplier_name,
			"supplier_part_no": supplier_name + " - " + item_code,
		}
	)

	supplier_item.save()
	item.append("supplier_items", supplier_item)
