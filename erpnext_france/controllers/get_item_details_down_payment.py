import frappe
from frappe import _
from erpnext.stock.get_item_details import get_item_details 
import json


@frappe.whitelist()
def get_item_details_down_payment(args, doc=None, for_validate=False, overwrite_warehouse=True):
	out = get_item_details(args, doc=None, for_validate=False, overwrite_warehouse=True)
	if out == None:
		return out
	
	item = frappe.get_doc('Item', out['item_code'])

	out["down_payment_rate"] = item.down_payment_percentage
	out["is_down_payment_item"] = item.is_down_payment_item

	return out