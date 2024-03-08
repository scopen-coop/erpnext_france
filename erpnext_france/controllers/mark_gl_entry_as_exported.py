import frappe
from frappe import _
import json
from frappe.utils.data import get_datetime

@frappe.whitelist()
def mark_gl_entry_as_exported(gl_entries):
    gl_entries = json.loads(gl_entries)
    date = get_datetime()

    for [gl_entry_name, export_date] in gl_entries:
        if not export_date:
            frappe.db.set_value('GL Entry', gl_entry_name, 'export_date', date, update_modified=False)

    return {
        'message': 'ok'
    }
