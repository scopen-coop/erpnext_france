import json

import frappe
from frappe import _
import re


def add_cards():
	add_card("ERPNext Settings", "ERPNext France")
	add_card("Accounting", "ERPNext France")


def add_card(workspace_name, workspace_link_label):
	workspace = frappe.get_doc('Workspace', workspace_name)
	workspace_link = frappe.get_last_doc(
		'Workspace Link',
		filters={'label': workspace_link_label, "parent": workspace_name}
	)

	content = json.loads(workspace.content)

	should_add_entry = True
	for element in content:
		if element['id'] == workspace_link.name:
			should_add_entry = False

	if not should_add_entry:
		return

	content.append({
		"id": workspace_link.name,
		"type": "card",
		"data": {
			"card_name": workspace_link.label,
			"col": 4
		}
	})

	workspace.content = json.dumps(content)
	workspace.save()
