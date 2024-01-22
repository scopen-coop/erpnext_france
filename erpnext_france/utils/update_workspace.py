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
