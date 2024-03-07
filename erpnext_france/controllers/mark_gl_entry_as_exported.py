import frappe
from frappe import _
import json
from frappe.utils import getdate, now
from datetime import datetime

@frappe.whitelist()
def mark_gl_entry_as_exported(gl_entries):
    gl_entries = json.loads(gl_entries)
    date = frappe.utils.data.get_datetime()
    for gl_entry_name in gl_entries:
        frappe.db.set_value('GL Entry', gl_entry_name, 'export_date', date, update_modified=False)

    return {
        'message': 'ok'
    }
