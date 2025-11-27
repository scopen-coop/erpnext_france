# Copyright (c) 2024 SCOPEN
# For license information, please see license.txt


import json
import os

import frappe
from erpnext.setup.setup_wizard.operations.taxes_setup import (
	from_detailed_data,
	update_regional_tax_settings,
)
from frappe import _


@frappe.whitelist(allow_guest=False)
def has_down_payment_item():
	if frappe.db.exists("Item", {"is_down_payment_item": 1}):
		return True
	return False


@frappe.whitelist(allow_guest=False)
def create_down_payment_item(company, item_group, income_account, expense_account=None):
	# Down payment Item Creation
	down_payment_item = frappe.new_doc("Item")
	down_payment_item.item_code = _("Down Payment Item")
	down_payment_item.item_name = _("Down Payment Item")
	down_payment_item.is_down_payment_item = 1
	down_payment_item.is_stock_item = 0
	down_payment_item.item_group = item_group
	down_payment_item.stock_uom = 'Unit'
	down_payment_item.insert(ignore_permissions=True)

	# Item default creation
	item_default = frappe.new_doc("Item Default")
	item_default.company = company
	item_default.income_account = income_account
	item_default.expense_account = expense_account
	item_default.parenttype = "Item"
	item_default.parent = down_payment_item.name
	item_default.parentfield = "item_defaults"
	item_default.save()

	down_payment_item.item_defaults.clear()
	down_payment_item.item_defaults.append(item_default)
	down_payment_item.save()
