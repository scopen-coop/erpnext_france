import frappe
import requests
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


class PappersAPI:
	def __init__(self):
		global_settings = frappe.get_single("Global Defaults")
		self.token = global_settings.get_password("pappers_api_key")

		self.headers = {"Content-Type": "application/json"}
		self.base_url = "https://api.pappers.fr/v2/"
		self.session = requests.Session()

	def get(self, params):
		query_params = {"api_token": self.token}

		if params:
			query_params.update(params)

		return self.session.get(self.url, headers=self.headers, params=query_params).json()


def setup_pappers(doc, method):
	if doc.pappers_api_key:
		setup_custom_fields()


def setup_custom_fields():

	pappers_fields = [
		dict(fieldname="public_information_tab", label="Public Information", fieldtype="Tab Break"),
		dict(
			fieldname="general_info_section",
			label="Company Type",
			fieldtype="Section Break",
			insert_after="public_information_tab",
			depends_on="eval:doc.code_naf",
		),
		dict(
			fieldname="code_naf",
			label="Code Naf",
			fieldtype="Data",
			insert_after="general_info_section",
			read_only=True,
		),
		dict(
			fieldname="libelle_code_naf",
			label="Libellé du Code Naf",
			fieldtype="Small Text",
			insert_after="code_naf",
			read_only=True,
		),
		dict(
			fieldname="general_info_section_col_break",
			fieldtype="Column Break",
			insert_after="libelle_code_naf",
		),
		dict(
			fieldname="domaine_activite",
			label="Domaine d'activité",
			fieldtype="Small Text",
			insert_after="general_info_section_col_break",
			read_only=True,
		),
		dict(
			fieldname="objet_social",
			label="Object Social",
			fieldtype="Small Text",
			insert_after="domaine_activite",
			read_only=True,
		),
		dict(
			fieldname="economie_sociale_solidaire",
			label="Entreprise de l'économie sociale et solidaire",
			fieldtype="Check",
			insert_after="objet_social",
			read_only=True,
		),
		dict(
			fieldname="creation_info_section",
			label="Company Creation",
			fieldtype="Section Break",
			insert_after="economie_sociale_solidaire",
			depends_on="eval:doc.date_creation",
		),
		dict(
			fieldname="date_creation",
			label="Date de création",
			fieldtype="Date",
			insert_after="creation_info_section",
			read_only=True,
		),
		dict(
			fieldname="creation_info_section_col_break",
			fieldtype="Column Break",
			insert_after="date_creation",
		),
		dict(
			fieldname="entreprise_cessee",
			label="Entreprise Fermée",
			fieldtype="Check",
			insert_after="creation_info_section_col_break",
			read_only=True,
		),
		dict(
			fieldname="date_cessation",
			label="Date de Cessation",
			fieldtype="Date",
			insert_after="entreprise_cessee",
			read_only=True,
			depends_on="eval:doc.entreprise_cessee",
		),
		dict(
			fieldname="rcs_info_section",
			label="RCS Information",
			fieldtype="Section Break",
			insert_after="date_cessation",
		),
		dict(
			fieldname="statut_rcs",
			label="Statut au RCS",
			fieldtype="Data",
			insert_after="rcs_info_section",
			read_only=True,
		),
		dict(
			fieldname="greffe", label="Greffe", fieldtype="Data", insert_after="statut_rcs", read_only=True
		),
		dict(fieldname="rcs_info_section_col_break", fieldtype="Column Break", insert_after="greffe"),
		dict(
			fieldname="numero_rcs",
			label="Numéro RCS",
			fieldtype="Data",
			insert_after="rcs_info_section_col_break",
			read_only=True,
		),
		dict(
			fieldname="date_immatriculation_rcs",
			label="Date d'immatriculation au RCS",
			fieldtype="Date",
			insert_after="numero_rcs",
			read_only=True,
		),
		dict(
			fieldname="date_premiere_immatriculation_rcs",
			label="Date de première immatriculation au RCS",
			fieldtype="Date",
			insert_after="date_immatriculation_rcs",
			read_only=True,
		),
		dict(
			fieldname="forme_juridique_info_section",
			label="Legal Form",
			fieldtype="Section Break",
			insert_after="date_premiere_immatriculation_rcs",
			depends_on="eval:doc.capital",
		),
		dict(
			fieldname="associe_unique",
			label="Associé Unique",
			fieldtype="Check",
			insert_after="forme_juridique_info_section",
			read_only=True,
		),
		dict(
			fieldname="forme_juridique",
			label="Forme Juridique",
			fieldtype="Data",
			insert_after="associe_unique",
			read_only=True,
		),
		dict(
			fieldname="forme_juridique_info_section_col_break",
			fieldtype="Column Break",
			insert_after="forme_juridique",
		),
		dict(
			fieldname="societe_a_mission",
			label="Société à mission",
			fieldtype="Check",
			insert_after="forme_juridique_info_section_col_break",
			read_only=True,
		),
		dict(
			fieldname="capital",
			label="Capital",
			fieldtype="Currency",
			insert_after="effectif",
			options="societe_a_mission",
			read_only=True,
		),
		dict(
			fieldname="devise_capital",
			label="Devise du capital",
			fieldtype="Data",
			insert_after="capital",
			hidden=True,
		),
		dict(
			fieldname="effectif_info_section",
			label="Headcount",
			fieldtype="Section Break",
			insert_after="devise_capital",
		),
		dict(
			fieldname="effectif",
			label="Effectif",
			fieldtype="Small Text",
			insert_after="effectif_info_section",
			read_only=True,
		),
		dict(
			fieldname="cloture_info_section",
			label="Accounting",
			fieldtype="Section Break",
			insert_after="effectif",
		),
		dict(
			fieldname="date_cloture_exercice",
			label="Date de clotûre de l'exercice",
			fieldtype="Data",
			insert_after="cloture_info_section",
			read_only=True,
		),
		dict(
			fieldname="cloture_info_section_col_break",
			fieldtype="Column Break",
			insert_after="date_cloture_exercice",
		),
		dict(
			fieldname="prochaine_date_cloture_exercice",
			label="Prochaine date de clotûre de l'exercice",
			fieldtype="Date",
			insert_after="cloture_info_section_col_break",
			read_only=True,
		),
		dict(
			fieldname="last_pappers_update",
			label="Last Update via Pappers",
			fieldtype="Date",
			insert_after="prochaine_date_cloture_exercice",
			hidden=True,
		),
		dict(
			fieldname="company_search",
			label="Company Search",
			fieldtype="Autocomplete",
			insert_after="naming_series",
			description="The search tool uses Pappers API.<br>You are limited to 100 searches per day.",
			allow_in_quick_entry=True,
		),
	]

	custom_fields = {
		"Customer": pappers_fields,
		"Supplier": pappers_fields,
	}

	create_custom_fields(custom_fields, ignore_validate=frappe.flags.in_patch, update=True)
