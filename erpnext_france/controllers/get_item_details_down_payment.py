import json

import frappe
from erpnext.stock.get_item_details import get_item_details
from frappe import _, get_hooks


@frappe.whitelist()
def get_item_details_down_payment(args, doc=None, for_validate=False, overwrite_warehouse=True):
	# find if other apps declare these override_whitelisted_methods
	# then get results from other hooks with this one
	hooks = get_hooks("override_whitelisted_methods", {}).get(
		"erpnext.stock.get_item_details.get_item_details", []
	)
	if hooks:
		current_method = __name__ + "." + get_item_details_down_payment.__name__
		current_hook_pos = hooks.index(current_method)
		if current_hook_pos > 0:
			method = frappe.get_attr(hooks[current_hook_pos - 1])
			out = method(args, doc, for_validate, overwrite_warehouse)
		else:
			# standard feature
			out = get_item_details(args, doc, for_validate, overwrite_warehouse)
	else:
		# standard feature
		out = get_item_details(args, doc, for_validate, overwrite_warehouse)

	if out is None:
		return out

	item = frappe.get_doc("Item", out["item_code"])

	out["down_payment_rate"] = item.get("down_payment_percentage")
	out["is_down_payment_item"] = item.get("is_down_payment_item")

	return out
