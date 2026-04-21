import os
import json
import frappe


def execute():
	if "erpnext_france" not in frappe.get_installed_apps():
		return

	if not frappe.db.table_exists("Code Naf"):
		return

	try:
		app_path = frappe.get_app_path("erpnext_france")
		json_path = os.path.join(app_path, "fixtures", "code_naf.json")

		if not os.path.exists(json_path):
			frappe.log_error(
				title="Pre migrate Code Naf",
				message=f"JSON file not found: {json_path}"
			)
			return

		with open(json_path) as f:
			data = json.load(f)

		codes = [item["code"] for item in data if "code" in item]

		if not codes:
			return

		deleted_count = frappe.db.count("Code Naf", {"code": ["in", codes]})
		frappe.db.delete("Code Naf", {"code": ["in", codes]})
		frappe.db.commit()

		print(f"[code_naf] {deleted_count} codes supprimés", flush=True)

	except Exception:
		frappe.log_error(
			title="Failed to pre migrate Code Naf",
			message=frappe.get_traceback()
		)