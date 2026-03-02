# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import json
import time
import unicodedata

import frappe
import requests
from frappe import _

logger = frappe.logger("scheduler")
logger.setLevel("INFO")

frappe.local.lang = "fr"


@frappe.whitelist()
def fetch_company_from_sirene(data):
	search_values = json.loads(data)
	nb_results = search_values["nb_results"]

	parameters = frappe.get_doc("ERPNext France Settings")

	if not parameters.api_url:
		return {"error": _("You have to specify an url for SIRENE API")}

	if not parameters.api_token:
		return {"error": _("You have to specify a token for SIRENE API")}

	filters = get_filters(search_values)
	if not filters:
		return {"error": _("You have to specify at least a filter for searching")}

	try:
		# Init connection with siren
		myToken = parameters.api_token
		myUrl = parameters.api_url + "/siret"

		headers = {
			"X-INSEE-Api-Key-Integration": format(myToken),
			"Accept": "application/json",
			"Content-Type": "application/x-www-form-urlencoded",
		}

		response = http_post(myUrl, headers=headers, data={"q": filters, "nombre": nb_results})

	except Exception as e:
		return {"error": _("Error during companies data recuperation:{0}").format(e)}

	return {"message": response}


def http_post(url, headers=None, body=None, data=None):
	try:
		response = requests.post(url=url, json=body, data=data, headers=headers)

		response = json.loads(response.content)
		if "fault" in response:
			frappe.throw(str(response["fault"]["description"]))

		if response["header"]["statut"] not in [201, 200]:
			if response["header"]["statut"] == 401:
				frappe.db.commit()
				frappe.throw(response["message"], title=_("SIRENE Error - Unauthorized"))
			elif response["header"]["statut"] == 403:
				frappe.msgprint(_("You didn't have permission to access this API"))
				frappe.throw(response["message"], title=_("SIRENE Error - Access Denied"))
			elif response["header"]["statut"] == 404:
				frappe.throw(response["header"]["message"], title=_("SIRENE Error - Not Found"))
			else:
				frappe.throw(response["header"]["reason"], title=response["header"]["statut"])

	except Exception as e:
		frappe.throw(str(type(e).__name__))

	return response


def get_filters(search_values):
	filters = []
	if "company_name" in search_values and search_values["company_name"] != "":
		filters.append('raisonSociale:"' + search_values["company_name"].replace('"', '\\"') + '"')

	if "siren" in search_values and search_values["siren"] != "":
		filters.append("siren:" + search_values["siren"])

	if "siret" in search_values and search_values["siret"] != "":
		filters.append("siret:" + search_values["siret"])

	if "naf" in search_values and search_values["naf"] != "":
		filters.append("activitePrincipaleUniteLegale:" + search_values["naf"])

	if "zipcode" in search_values and search_values["zipcode"] != "":
		filters.append("codePostalEtablissement:" + search_values["zipcode"])

	filters.append("-periode(etatAdministratifEtablissement:F)")

	return " AND ".join(filters)


@frappe.whitelist()
def fetch_company_from_siret_or_siren(data):
	search_value = json.loads(data)

	if not search_value:
		return {"error": _("Siren or Siret is required to check updates")}

	search_key = next(iter(search_value.keys()))

	parameters = frappe.get_doc("ERPNext France Settings")

	if not parameters.api_url:
		return {"error": _("You have to specify an url for SIRENE API")}

	if not parameters.api_token:
		return {"error": _("You have to spgecify a token for SIRENE API")}

	filters = get_filters(search_value)
	if not filters:
		return {"error": _("You have to specify at least a filter for searching")}

	try:
		# Init connection with siren
		myToken = parameters.api_token
		myUrl = parameters.api_url + "/siret"

		headers = {
			"X-INSEE-Api-Key-Integration": format(myToken),
			"Accept": "application/json",
			"Content-Type": "application/x-www-form-urlencoded",
		}

		response = http_post(myUrl, headers=headers, data={"q": filters, search_key: search_value})

	except Exception as e:
		return {"error": _("Error during companies data recuperation:{0}").format(e)}

	return {"message": response}


@frappe.whitelist()
def execute_sirene_check():
	"""
	Logique métier de comparaison des données sirene
	"""

	results = {
		"processed_customer": 0,
		"processed_supplier": 0,
		"skipped": 0,
		"errors_customer": 0,
		"errors_supplier": 0,
		"updates": {},
		"logs": [],
	}

	logger.info("=== Starting SIREN Update Check ===")
	print("=== Starting SIREN Update Check ===")
	results["logs"].append("=" * 30 + " Starting SIREN Update Check " + "=" * 30)
	results["logs"].append(f"Started at: {frappe.utils.now()}\n")

	if frappe.cache().get_value("siren_update_running"):
		logger.info("Task already running, exiting")
		results["logs"].append("Task already running, skipped")
		print("Task already running, skipped")
		return results

	frappe.cache().set_value("siren_update_running", True, expires_in_sec=7200)

	doctypes = [
		{
			"type": "Customer",
			"field_name": "customer_name",
			"field_type": "customer_type",
			"field_address": "customer_primary_address",
			"processed": 0,
			"update": 0,
		},
		{
			"type": "Supplier",
			"field_name": "supplier_name",
			"field_type": "supplier_type",
			"field_address": "supplier_primary_address",
			"processed": 0,
			"update": 0,
		},
	]

	for doctype in doctypes:
		results["logs"].append(f"\n{'#' * 10} Processing {doctype['type']}s")

		elements = frappe.get_all(
			doctype["type"],
			filters=[[doctype["type"], "siret", "!=", ""]],
			or_filters=[[doctype["type"], "siren", "!=", ""]],
			fields=[
				doctype["field_name"],
				doctype["field_type"],
				"name",
				"siren",
				"siret",
				"code_naf",
				"legal_form",
				"tax_id",
				doctype["field_address"],
			],
		)

		results["logs"].append(f"Found {len(elements)} {doctype['type']} to check\n")

		if len(elements) == 0:
			continue

		results["updates"][doctype["type"]] = []

		for idx, element in enumerate(elements, 1):
			try:
				results["processed_" + doctype["type"].lower()] += 1

				siret = element.get("siret")
				siren = element.get("siren")

				if siret:
					query_data = {"data": {"siret": siret}, "type": "SIRET", "value": siret}
				elif siren:
					query_data = {"data": {"siren": siren}, "type": "SIREN", "value": siren}
				else:
					results["skipped"] += 1
					results["logs"].append(f"\n{idx}. {element[doctype['field_name']]}")
					results["logs"].append("Skipped: No SIRET or SIREN")
					continue

				results["logs"].append(f"{idx}. {element[doctype['field_name']]}")
				results["logs"].append(f"Calling {query_data['type']}: {query_data['value']}")

				data_to_post = {
					query_data["type"].lower(): query_data["value"],
					"nb_results": 1,
				}

				response = fetch_company_from_sirene(json.dumps(data_to_post))
				entity = response["message"]["etablissements"][0]

				if (results["processed_customer"] + results["processed_customer"]) % 25 == 0:
					print("Pause")
					time.sleep(5)

				if entity:
					logger.info(f"{doctype['type']} {element[doctype['field_name']]} - Data found")
					results["logs"].append("Data found from API")

					address = None
					if element[doctype["field_address"]]:
						address = frappe.get_doc("Address", element[doctype["field_address"]])

					entity_info = get_entity_info(entity, 0)

					if address:
						match = compare_values(doctype, element, address.as_dict(), entity_info)

						if not match:
							results["updates"][doctype["type"]].append(
								{
									"name": element["name"],
									"display_name": element[doctype["field_name"]],
									"new_data": entity_info,
									"current_data": element,
								}
							)

					else:
						results["skipped"] += 1
						results["logs"].append("No address returned from ErpNext API")

				else:
					results["skipped"] += 1
					results["logs"].append("No entity returned from API")

				results["logs"].append("\n")

			except Exception as e:
				frappe.cache().delete_value("siren_update_running")
				results["errors_" + doctype["type"].lower()] += 1
				error_msg = str(e)
				logger.error(f"Error processing {element[doctype['field_name']]}: {error_msg}")
				results["logs"].append(f"Error: {error_msg}\n")
				frappe.log_error(message=frappe.get_traceback(), title=f"SIREN API Error: {element.name}")

		results["logs"].append("\n" + "=" * 50)

	results["logs"].append("\nSUMMARY")
	results["logs"].append("=" * 50)
	results["logs"].append(f"Processed: {results['processed_customer']}")
	results["logs"].append(f"Processed: {results['processed_supplier']}")
	results["logs"].append(f"Skipped: {results['skipped']}")
	results["logs"].append(f"Errors: {results['errors_customer']}")
	results["logs"].append(f"Errors: {results['errors_supplier']}")

	total_updates = sum(len(updates) for updates in results["updates"].values())
	results["logs"].append(f"Updates detected: {total_updates}")

	results["logs"].append(f"\nCompleted at: {frappe.utils.now()}")

	logger.info(
		f"Task completed: {(results['errors_customer'] + results['errors_supplier'])} processed, {(results['errors_customer'] + results['errors_supplier'])} errors"
	)

	frappe.cache().delete_value("siren_update_running")
	results["logs"].append("\nCache lock released")

	return results


@frappe.whitelist()
def compare_values(doctype, element, address, entity_info):
	if isinstance(doctype, str):
		doctype = json.loads(doctype)
	if isinstance(element, str):
		element = json.loads(element)
	if isinstance(address, str):
		address = json.loads(address)
	if isinstance(entity_info, str):
		entity_info = json.loads(entity_info)

	match = True
	match &= match and compare_value(element[doctype["field_name"]], entity_info["company_name"])
	match &= match and compare_value(element[doctype["field_type"]], entity_info["entity_type"])
	match &= match and compare_value(address["address_line1"], entity_info["address_1"])
	match &= match and compare_value(address["pincode"], entity_info["zipcode"])
	match &= match and compare_value(address["city"], entity_info["town"])
	match &= match and compare_value(address["country"], entity_info["country"])
	match &= match and compare_value(element["siren"], entity_info["siren"])
	match &= match and compare_value(element["siret"], entity_info["siret"])
	match &= match and compare_value(element["code_naf"], entity_info["code_naf"])
	match &= match and compare_value(element["tax_id"], entity_info["tax_id"])
	match &= match and compare_value(element["legal_form"], entity_info["legal_form"])

	return match


def compare_value(dval, sval):
	match = True
	match &= match and (local_compare(dval) == local_compare(sval))
	return match


@frappe.whitelist()
def get_entity_info(entity, i):
	if isinstance(entity, str):
		entity = json.loads(entity)

	company_name_alias = ""
	company_name_all = ""
	date_creation = ""
	address_1 = ""
	town = ""
	zipcode = ""
	country = "France"
	siren = ""
	siret = ""
	code_naf = ""
	entity_type = ""
	legal_form = ""

	if is_not_null(entity["uniteLegale"]["denominationUniteLegale"]) and entity["uniteLegale"][
		"nomUsageUniteLegale"
	] in [None, "[ND]", ""]:
		# Morale
		entity_type = "Company"
		company_name = entity["uniteLegale"]["denominationUniteLegale"]

		if is_not_null(entity["uniteLegale"]["denominationUsuelle1UniteLegale"]):
			company_name_alias = entity["uniteLegale"]["denominationUsuelle1UniteLegale"]
		elif is_not_null(entity["uniteLegale"]["denominationUsuelle2UniteLegale"]):
			company_name_alias = entity["uniteLegale"]["denominationUsuelle2UniteLegale"]
		elif is_not_null(entity["periodesEtablissement"][0]):
			entityinfo = entity["periodesEtablissement"][0]
			company_name_alias = entityinfo["denominationUsuelleEtablissement"]

			if not is_not_null(company_name_alias):
				if is_not_null(entityinfo["enseigne1Etablissement"]):
					company_name_alias = entityinfo["enseigne1Etablissement"]
				elif is_not_null(entityinfo["enseigne2Etablissement"]):
					company_name_alias = entityinfo["enseigne2Etablissement"]
				elif is_not_null(entityinfo["enseigne3Etablissement"]):
					company_name_alias = entityinfo["enseigne3Etablissement"]

		if company_name == company_name_alias:
			company_name_alias = ""

		company_name_all = company_name

	else:
		# Physique
		entity_type = "Individual"
		company_name = entity["uniteLegale"]["nomUsageUniteLegale"]
		firstname = entity["uniteLegale"]["prenomUsuelUniteLegale"]
		if not firstname:
			if is_not_null(entity["uniteLegale"]["prenom1UniteLegale"]):
				firstname = entity["uniteLegale"]["prenom1UniteLegale"]
			elif is_not_null(entity["uniteLegale"]["prenom2UniteLegale"]):
				firstname = entity["uniteLegale"]["prenom2UniteLegale"]
			elif is_not_null(entity["uniteLegale"]["prenom3UniteLegale"]):
				firstname = entity["uniteLegale"]["prenom3UniteLegale"]
			elif is_not_null(entity["uniteLegale"]["prenom4UniteLegale"]):
				firstname = entity["uniteLegale"]["prenom4UniteLegale"]

		else:
			if is_not_null(entity["uniteLegale"]["prenom1UniteLegale"]):
				company_name_alias = entity["uniteLegale"]["prenom1UniteLegale"]
			elif is_not_null(entity["uniteLegale"]["prenom2UniteLegale"]):
				company_name_alias = entity["uniteLegale"]["prenom2UniteLegale"]
			elif is_not_null(entity["uniteLegale"]["prenom3UniteLegale"]):
				company_name_alias = entity["uniteLegale"]["prenom3UniteLegale"]
			elif is_not_null(entity["uniteLegale"]["prenom4UniteLegale"]):
				company_name_alias = entity["uniteLegale"]["prenom4UniteLegale"]

		company_name_all = firstname + " " if firstname else "" + (company_name if company_name else "")

	if is_not_null(company_name_alias):
		company_name_all += " (" + company_name_alias + ")"

	if is_not_null(entity["dateCreationEtablissement"]):
		date_creation = entity["dateCreationEtablissement"]

	if is_not_null(entity["adresseEtablissement"]["numeroVoieEtablissement"]):
		address_1 = entity["adresseEtablissement"]["numeroVoieEtablissement"]

	if entity["adresseEtablissement"]["typeVoieEtablissement"]:
		address_1 += " " + entity["adresseEtablissement"]["typeVoieEtablissement"]

	if is_not_null(entity["adresseEtablissement"]["libelleVoieEtablissement"]):
		address_1 += " " + entity["adresseEtablissement"]["libelleVoieEtablissement"]

	if is_not_null(entity["adresseEtablissement"]["complementAdresseEtablissement"]):
		address_1 += " " + entity["adresseEtablissement"]["complementAdresseEtablissement"]

	if is_not_null(entity["adresseEtablissement"]["libelleCommuneEtablissement"]):
		town = entity["adresseEtablissement"]["libelleCommuneEtablissement"]
	elif is_not_null(entity["adresseEtablissement"]["libelleCommuneEtrangerEtablissement"]):
		town = entity["adresseEtablissement"]["libelleCommuneEtrangerEtablissement"]

	if is_not_null(entity["adresseEtablissement"]["codePostalEtablissement"]):
		zipcode = entity["adresseEtablissement"]["codePostalEtablissement"]

	if is_not_null(entity["adresseEtablissement"]["libellePaysEtrangerEtablissement"]):
		country = entity["adresseEtablissement"]["libellePaysEtrangerEtablissement"]

	if is_not_null(entity["siren"]):
		siren = entity["siren"]

	if is_not_null(entity["siret"]):
		siret = entity["siret"]

	if is_not_null(entity["uniteLegale"]["activitePrincipaleUniteLegale"]):
		code_naf = entity["uniteLegale"]["activitePrincipaleUniteLegale"]
		code_naf = code_naf.replace(".", "")

	if is_not_null(entity["uniteLegale"]["categorieJuridiqueUniteLegale"]):
		legal_form = entity["uniteLegale"]["categorieJuridiqueUniteLegale"]

	# intra - community vat number calculation (12 + 3 * (SIREN modulo 97)) modulo 97
	coef = 97
	vat_intra_calc = int(siren) % coef
	vat_intra_calc2 = left_fill_num((12 + 3 * vat_intra_calc) % coef, 2)
	tva_intra = "FR" + vat_intra_calc2 + siren

	entity_info = {
		"company_name": company_name_all,
		"entity_type": entity_type,
		"address_1": address_1,
		"zipcode": zipcode,
		"town": town,
		"country": country,
		"date_creation": date_creation,
		"siren": siren,
		"siret": siret,
		"code_naf": code_naf,
		"legal_form": legal_form,
		"tax_id": tva_intra,
		"id": i,
	}

	return entity_info


def send_sirene_report(results, recipients_customer, recipients_supplier, site_url, subject=None):
	total_updates_customers = len(results["updates"]["Customer"])
	total_updates_suppliers = len(results["updates"]["Supplier"])

	customer_sent = False
	supplier_sent = False

	if total_updates_customers > 0 or results["errors_customer"] > 0:
		try:
			email_content = frappe.render_template(
				"templates/emails/sirene_update_report.html",
				{
					"updates": results["updates"]["Customer"],
					"errors": results["errors_customer"],
					"processed": results["processed_customer"],
					"doctype": "Customer",
					"site_url": site_url,
				},
			)

			frappe.sendmail(
				recipients=recipients_customer,
				subject=subject,
				message=email_content,
				now=True,
			)

			logger.info("Customers report successfully sent by email")
			customer_sent = True

		except Exception as e:
			logger.error(f"Error sending email: {e!s}")
			frappe.log_error(message=frappe.get_traceback(), title="SIREN Customers report Email Error")
			return False

	if total_updates_suppliers > 0 or results["errors_supplier"] > 0:
		try:
			email_content = frappe.render_template(
				"templates/emails/sirene_update_report.html",
				{
					"updates": results["updates"]["Supplier"],
					"errors": results["errors_supplier"],
					"processed": results["processed_supplier"],
					"doctype": "Supplier",
					"site_url": site_url,
				},
			)

			frappe.sendmail(
				recipients=recipients_supplier,
				subject=subject,
				message=email_content,
				now=True,
			)

			logger.info("Suppliers report successfully sent by email")
			supplier_sent = True

		except Exception as e:
			logger.error(f"Error sending email: {e!s}")
			frappe.log_error(message=frappe.get_traceback(), title="SIREN Suppliers report Email Error")
			return False

	return customer_sent or supplier_sent


def local_compare(text):
	"""Remove accents from text"""
	nfkd = unicodedata.normalize("NFKD", text)
	return "".join([c for c in nfkd if not unicodedata.combining(c)])


def left_fill_num(num, target_length):
	val = str(num)
	return val.rjust(target_length, "0")


def is_not_null(val):
	return val not in [None, "[ND]", ""]
