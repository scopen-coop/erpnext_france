import json

import frappe
from frappe import _
import re


def add_cards():
	add_card("ERPNext Settings", "ERPNext France")
	add_card("Accounting", "ERPNext France")
	update_workspace_link_idx()


def add_card(workspace_name, workspace_link_label):
	workspace = frappe.get_doc('Workspace', workspace_name)

	if not workspace:
		return

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


def update_workspace_link_idx():
	workspace_link_idx = [
		{
			"name": "463658a38e",
			"idx": 70
		},
		{
			"name": "87e757e3c1",
			"idx": 71
		},
		{
			"name": "dc2d70f0be",
			"idx": 72
		},
		{
			"name": "2faa60a916",
			"idx": 73
		},
		{
			"name": "df2fa6d850",
			"idx": 74
		},
		{
			"name": "a129c62bb0",
			"idx": 75
		},
		{
			"name": "fc83fdfd07",
			"idx": 110
		},
		{
			"name": "24d4382374",
			"idx": 111
		},
		{
			"name": "df2fa6d847",
			"idx": 112
		},
	]
	for workspace_info in workspace_link_idx:
		if not frappe.db.exists("Workspace Link", dict(name=workspace_info['name'])):
			continue

		workspace_link  = frappe.get_doc('Workspace Link', workspace_info['name'])
		workspace_link.idx =  workspace_info['idx']
		workspace_link.save()
