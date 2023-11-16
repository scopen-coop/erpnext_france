import frappe
from frappe import _
from frappe.utils import cint, date_diff, nowdate

from erpnext_france.regional.france.pappers.entreprise import PappersEntreprise
from erpnext_france.regional.france.pappers.recherche import PappersRecherche


def validate(doc, method):
	meta = frappe.get_meta(doc.doctype)
	if meta.has_field("siren_number"):
		get_siren_from_tax_id(doc)
		get_info_from_pappers(doc)


def get_siren_from_tax_id(doc):
	if doc.tax_id and not doc.get("siren_number"):
		doc.siren_number = doc.tax_id[4:]


def get_info_from_pappers(doc):
	global_defauts = frappe.get_single("Global Defaults")
	if not global_defauts.pappers_api_key:
		return

	if date_diff(nowdate(), doc.last_pappers_update) > cint(global_defauts.pappers_update_interval):
		return

	data = PappersEntreprise().get({"siren": doc.siren_number})

	if data:
		update_tax_id(doc, data.get("numero_tva_intracommunautaire"))

		meta = frappe.get_meta(doc.doctype)
		for key, value in data.items():
			if meta.has_field(key):
				doc.set(key, value)

		doc.last_pappers_update = nowdate()


def update_tax_id(doc, vat_number):
	if not doc.tax_id:
		doc.tax_id = vat_number

	elif doc.tax_id != vat_number:
		frappe.msgprint(
			_(
				"The VAT number registered in this document doesn't match the VAT number available publicly for this company: {0}".format(
					vat_number
				)
			)
		)


@frappe.whitelist()
def company_query(txt):
	if txt:
		res = PappersRecherche().get(
			{"q": txt, "cibles": "nom_entreprise,siren,siret", "longueur": 100, "api_token": None}
		)

		if res.get("statusCode") == 401:
			# TODO: Handle when all tokens have been used
			return []

		if res:
			return list(
				{
					"label": r.get("nom_entreprise"),
					"value": r.get("siren"),
					"description": f"SIREN: {r.get('siren_formate')}<br>{r.get('siege', {}).get('adresse_ligne_1', '')} {r.get('siege', {}).get('code_postal', '')} {r.get('siege', {}).get('ville', '')}",
				}
				for r in res.get("resultats_nom_entreprise", [])
			)

	return []
