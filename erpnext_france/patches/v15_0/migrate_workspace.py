# Copyright (c) 2024, Scopen and contributors
# For license information, please see license.txt


import frappe


def execute():
    if "erpnext_france" in frappe.get_installed_apps():
        try:
            frappe.db.sql(
                "delete from `tabWorkspace Link` WHERE parent='ERPNext Settings' and only_for='France'"
            )
            frappe.db.sql(
                "delete from `tabWorkspace Link` WHERE label='ERPNext France' and only_for='France'"
            )
            frappe.db.sql(
                "delete from `tabWorkspace Link` WHERE parent='Accounting' and only_for='France'"
            )

        except Exception:
            frappe.log_error("Failed to migrate France Workspace.")
