# Copyright (c) 2024, Scopen and contributors
# For license information, please see license.txt


import frappe


def execute():
    if "erpnext_france" in frappe.get_installed_apps():
        try:
            frappe.db.sql(
                "delete from `tabWorkspace Link` WHERE parent='ERPNext Settings'"
            )
            frappe.db.sql(
                "delete from `tabWorkspace Link` WHERE label='ERPNext France'"
            )
            frappe.db.sql(
                "delete from `tabWorkspace Link` WHERE only_for='France' and parent='Accounting'"
            )

        except Exception:
            frappe.log_error("Failed to migrate France Workspace.")
