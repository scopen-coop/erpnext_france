import json

import frappe
from frappe import _
import re

# TODO: Actuellement ne marche pas voir si l'on fait ça ou une PR dans FRAPPE
def execute(aa,bb):
	regexShortcut = re.compile(r"^.*Your Shortcuts.*$", re.IGNORECASE)
	regexReport = re.compile(r"^.*Reports & Masters.*$", re.IGNORECASE)
	for seq, workspace in enumerate(frappe.get_all("Workspace")):
		doc = frappe.get_doc("Workspace", workspace.name)
		content = json.loads(doc.content)
		modified = False
		for section in content:
			if not 'data' in section or not 'text' in section['data']:
				continue

			section['data']['text'] = regexShortcut.sub(_('Your Shortcuts'), section['data']['text'])
			section['data']['text'] = regexReport.sub('Reports et Masters', section['data']['text'])
			modified = True

		if modified:
			doc.db_set('content', str(content))


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
