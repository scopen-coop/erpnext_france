import frappe
from frappe import _
from erpnext.stock.get_item_details import get_uom_conv_factor

def on_update(doc, method):
	old_doc = doc.get_doc_before_save()
	if not old_doc:
		return

	if doc.stock_uom == old_doc.stock_uom:
		return

	if len(doc.eco_part) == 0:
		return

	conversion_factor = get_uom_conv_factor(old_doc.stock_uom, doc.stock_uom)
	if not conversion_factor:
		# Vérifier si l'UOM saisie correspond à une unité de conversion
		for detail in old_doc.uoms:
			if detail.uom == doc.stock_uom:
				conversion_factor = detail.conversion_factor

	if not conversion_factor:
		frappe.throw(_('Cannot Update EcoPart because there is no conversion factor between units'))

	for ecopart in doc.eco_part:
		ecopart.amount /= conversion_factor
		ecopart.save()
