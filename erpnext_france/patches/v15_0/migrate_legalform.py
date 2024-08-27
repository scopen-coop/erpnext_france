# Copyright (c) 2024, Scopen and contributors
# For license information, please see license.txt


import frappe


def execute():
    if "erpnext_france" in frappe.get_installed_apps():
        try:
            frappe.db.sql("update `tabLegal Form` set title=CONCAT(code,' - ',label)")

        except Exception:
            frappe.log_error("Failed to migrate Code Naf.")
