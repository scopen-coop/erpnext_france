import frappe
import json


def execute():
    if "erpnext_france" in frappe.get_installed_apps():
        try:
            with open("apps/erpnext_france/erpnext_france/fixtures/code_naf.json") as f:
                data = json.load(f)

            codes = [item["code"] for item in data]

            frappe.db.delete("Code NAF", {"code": ["in", codes]})
            frappe.db.commit()

        except Exception:
            frappe.log_error("Failed to pre migrate Code Naf.")

