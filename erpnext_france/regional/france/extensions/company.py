import frappe
from frappe import _

from erpnext_france.regional.france.pappers.document import PappersDocument


@frappe.whitelist()
def get_extrait_pappers(siren):
	response = PappersDocument().get_extrait_pappers(siren)

	if response.status_code == 401:
		frappe.redirect_to_message(
			_("Document Unavailable"),
			_(
				"You have reached your API requests limit for this month.<br>Please buy additional tokens at pappers.fr"
			),
		)
		frappe.local.flags.redirect_location = frappe.local.response.location
	else:
		frappe.local.response.filename = f"{siren}.pdf"
		frappe.local.response.filecontent = response.content
		frappe.local.response.type = "pdf"


@frappe.whitelist()
def get_extrait_inpi(siren):
	response = PappersDocument().get_extrait_inpi(siren)

	if response.status_code == 401:
		frappe.redirect_to_message(
			_("Document Unavailable"),
			_(
				"You have reached your API requests limit for this month.<br>Please buy additional tokens at pappers.fr"
			),
		)
		frappe.local.flags.redirect_location = frappe.local.response.location
	else:
		frappe.local.response.filename = f"{siren}.pdf"
		frappe.local.response.filecontent = response.content
		frappe.local.response.type = "pdf"


@frappe.whitelist()
def get_extrait_insee(siren):
	response = PappersDocument().get_extrait_insee(siren)

	if response.status_code == 401:
		frappe.redirect_to_message(
			_("Document Unavailable"),
			_(
				"You have reached your API requests limit for this month.<br>Please buy additional tokens at pappers.fr"
			),
		)
		frappe.local.flags.redirect_location = frappe.local.response.location
	else:
		frappe.local.response.filename = f"{siren}.pdf"
		frappe.local.response.filecontent = response.content
		frappe.local.response.type = "pdf"
