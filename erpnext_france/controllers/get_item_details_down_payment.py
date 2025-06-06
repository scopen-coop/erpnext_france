import json

import frappe
from erpnext.stock.get_item_details import get_item_details
from frappe import _


@frappe.whitelist()
def get_item_details_down_payment(args, doc=None, for_validate=False, overwrite_warehouse=True):
	out = get_item_details(args, doc, for_validate, overwrite_warehouse)
	if out is None:
		return out

	item = frappe.get_doc("Item", out["item_code"])

	out["down_payment_rate"] = item.down_payment_percentage
	out["is_down_payment_item"] = item.is_down_payment_item

	return out
