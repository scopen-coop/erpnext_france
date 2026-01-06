# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import json
import unicodedata
import frappe
import requests
from frappe import _


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
    search_key = list(search_value.keys())[0]

    parameters = frappe.get_doc("ERPNext France Settings")

    if not parameters.api_url:
        return {"error": _("You have to specify an url for SIRENE API")}

    if not parameters.api_token:
        return {"error": _("You have to specify a token for SIRENE API")}

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
def compare_values(doctype, element, address, entity):
    entity_info = get_entity_info(entity, 1)
    match = True
    match &= match and compare_value(element[doctype['field_name']] , entity_info['company_name'])
    match &= match and compare_value(element[doctype['field_type']] , entity_info['entity_type'])
    match &= match and compare_value(address['address_line1'] , entity_info['address_1'])
    match &= match and compare_value(address['pincode'] , entity_info['zipcode'])
    match &= match and compare_value(address['city'] , entity_info['town'])
    match &= match and compare_value(address['country'] , entity_info['country'])
    match &= match and compare_value(element['siren'] , entity_info['siren'])
    match &= match and compare_value(element['siret'] , entity_info['siret'])
    match &= match and compare_value(element['code_naf'] , entity_info['code_naf'])
    match &= match and compare_value(element['tax_id'] , entity_info['tax_id'])
    match &= match and compare_value(element['legal_form'] , entity_info['legal_form'])

    return match

def compare_value(dval, sval):
    match = True
    match &= match and (local_compare(dval) == local_compare(sval))
    return match

def get_entity_info(entity, i):
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

    if (entity['uniteLegale']['denominationUniteLegale'] not in [None, '[ND]', ''] and
        entity['uniteLegale']['nomUsageUniteLegale'] in [None, '[ND]', '']):
        # Morale
        entity_type = "Company"
        company_name = entity["uniteLegale"]["denominationUniteLegale"]

        if entity["uniteLegale"]["denominationUsuelle1UniteLegale"] not in [None, '[ND]', '']:
            company_name_alias = entity["uniteLegale"]["denominationUsuelle1UniteLegale"]
        elif entity["uniteLegale"]["denominationUsuelle2UniteLegale"] not in [None, '[ND]', '']:
            company_name_alias = entity["uniteLegale"]["denominationUsuelle2UniteLegale"]
        elif entity["uniteLegale"]["denominationUsuelle2UniteLegale"] not in [None, '[ND]', '']:
            company_name_alias = entity["uniteLegale"]["denominationUsuelle2UniteLegale"]
        elif entity["periodesEtablissement"][0] not in [None, '[ND]', '']:
            entityinfo = entity["periodesEtablissement"][0]
            company_name_alias = entityinfo["denominationUsuelleEtablissement"]

            if not company_name_alias not in [None, '[ND]', '']:
                if entityinfo["enseigne1Etablissement"] not in [None, '[ND]', '']:
                    company_name_alias = entityinfo["enseigne1Etablissement"]
                elif entityinfo["enseigne2Etablissement"] not in [None, '[ND]', '']:
                    company_name_alias = entityinfo["enseigne2Etablissement"]
                elif entityinfo["enseigne3Etablissement"] not in [None, '[ND]', '']:
                    company_name_alias = entityinfo["enseigne3Etablissement"]


        if company_name == company_name_alias :
            company_name_alias = ""

        company_name_all = company_name

    else :
        # Physique
        entity_type = "Individual"
        company_name = entity["uniteLegale"]["nomUsageUniteLegale"]
        firstname = entity["uniteLegale"]["prenomUsuelUniteLegale"]

        if not firstname :
            if entity["uniteLegale"]["prenom1UniteLegale"] not in [None, '[ND]', '']:
                firstname = entity["uniteLegale"]["prenom1UniteLegale"]
            elif entity["uniteLegale"]["prenom2UniteLegale"] not in [None, '[ND]', '']:
                firstname = entity["uniteLegale"]["prenom2UniteLegale"]
            elif entity["uniteLegale"]["prenom3UniteLegale"] not in [None, '[ND]', '']:
                firstname = entity["uniteLegale"]["prenom3UniteLegale"]
            elif    entity["uniteLegale"]["prenom4UniteLegale"] not in [None, '[ND]', '']:
                firstname = entity["uniteLegale"]["prenom4UniteLegale"]

        else :
            if entity["uniteLegale"]["prenom1UniteLegale"] not in [None, '[ND]', '']:
                company_name_alias = entity["uniteLegale"]["prenom1UniteLegale"]
            elif entity["uniteLegale"]["prenom2UniteLegale"] not in [None, '[ND]', '']:
                company_name_alias = entity["uniteLegale"]["prenom2UniteLegale"]
            elif entity["uniteLegale"]["prenom3UniteLegale"] not in [None, '[ND]', '']:
                company_name_alias = entity["uniteLegale"]["prenom3UniteLegale"]
            elif entity["uniteLegale"]["prenom4UniteLegale"] not in [None, '[ND]', '']:
                company_name_alias = entity["uniteLegale"]["prenom4UniteLegale"]

        company_name_all = firstname + " " + (company_name if company_name else "")

    if company_name_alias not in [None, '[ND]', '']:
        company_name_all += " (" + company_name_alias + ")"

    if entity['dateCreationEtablissement'] not in [None, '[ND]', ''] :
        date_creation = entity['dateCreationEtablissement']

    if entity['adresseEtablissement']['numeroVoieEtablissement'] not in [None, '[ND]', ''] :
        address_1 = entity['adresseEtablissement']['numeroVoieEtablissement']

    if entity['adresseEtablissement']['typeVoieEtablissement'] :
        address_1 += " " + entity['adresseEtablissement']['typeVoieEtablissement']

    if entity['adresseEtablissement']['libelleVoieEtablissement'] not in [None, '[ND]', ''] :
        address_1 += " " + entity['adresseEtablissement']['libelleVoieEtablissement']

    if entity['adresseEtablissement']['complementAdresseEtablissement'] not in [None, '[ND]', ''] :
        address_1 +=" " + entity['adresseEtablissement']['complementAdresseEtablissement']

    if entity['adresseEtablissement']['libelleCommuneEtablissement'] not in [None, '[ND]', ''] :
        town = entity['adresseEtablissement']['libelleCommuneEtablissement']
    elif entity['adresseEtablissement']['libelleCommuneEtrangerEtablissement'] not in [None, '[ND]', ''] :
       town = entity['adresseEtablissement']['libelleCommuneEtrangerEtablissement']

    if entity['adresseEtablissement']['codePostalEtablissement'] not in [None, '[ND]', ''] :
        zipcode = entity['adresseEtablissement']['codePostalEtablissement']

    if entity['adresseEtablissement']['libellePaysEtrangerEtablissement'] not in [None, '[ND]', ''] :
        country = entity['adresseEtablissement']['libellePaysEtrangerEtablissement']

    if entity['siren'] not in [None, '[ND]', '']:
        siren = entity['siren']

    if entity['siret'] not in [None, '[ND]', '']:
        siret = entity['siret']

    if entity['uniteLegale']['activitePrincipaleUniteLegale'] not in [None, '[ND]', '']:
        code_naf = entity['uniteLegale']['activitePrincipaleUniteLegale']
        code_naf = code_naf.replace(".", "")

    if entity['uniteLegale']['categorieJuridiqueUniteLegale'] not in [None, '[ND]', '']:
        legal_form = entity['uniteLegale']['categorieJuridiqueUniteLegale']

    # intra - community vat number calculation
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

def local_compare(text):
    """Remove accents from text"""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])

def left_fill_num(num, target_length) :
    val = str(num)
    return val.rjust(target_length, '0')

