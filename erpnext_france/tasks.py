import unicodedata
import json

import frappe
import requests
from requests.exceptions import RequestException, Timeout
from frappe import _

logger = frappe.logger("scheduler")
logger.setLevel("INFO")

MAIL_SUBJECT = _("SIRENE - Updates available")
PICTO_MAGNIFIER = "https://cdn.iconscout.com/icon/free/png-256/free-magnifying-glass-icon-svg-download-png-1798586.png"
MAIL_TO = ["support@example.com"]
MAIL_BODY_HEADER = _("Updates available for the entities below:")


def check_sirene_update():
    """
    Création du Scheduled Job Log
    """
    job_log = create_job_log('check_sirene_update')

    try:
        result = _execute_sirene_update()
        complete_job_log(job_log, status='Complete', details=result)

    except Exception as e:
        error_details = f"Fatal Error: {str(e)}\n\n{frappe.get_traceback()}"
        complete_job_log(job_log, status='Failed', details=error_details)

        frappe.log_error(frappe.get_traceback(), "SIREN Update Task Failed")


def create_job_log(method_name):
    """
    Créer un Scheduled Job Log
    """

    job_type_name = frappe.db.get_value('Scheduled Job Type', {'method': f'erpnext_france.tasks.{method_name}'}, 'name')

    if not job_type_name:
        job_type = frappe.get_doc({
            'doctype': 'Scheduled Job Type',
            'method': f'erpnext_france.tasks.{method_name}',
            'frequency': 'Daily'
        })
        job_type.insert(ignore_permissions=True)
        frappe.db.commit()
        job_type_name = job_type.name

    job_log = frappe.get_doc({
        'doctype': 'Scheduled Job Log',
        'scheduled_job_type': job_type_name,
        'status': 'Scheduled',
        'details': f'Started at {frappe.utils.now()}'
    })
    job_log.insert(ignore_permissions=True)
    frappe.db.commit()
    return job_log


def complete_job_log(job_log, status, details):
    """
    Finaliser le Scheduled Job Log
    """
    job_log.reload()
    job_log.status = status
    job_log.details = details
    job_log.save(ignore_permissions=True)
    frappe.db.commit()


def _execute_sirene_update():
    """
    Logique métier de comparaison des données sirene
    """
    mail_body = "<h5>" + MAIL_BODY_HEADER + "</h5>"
    log_details = []

    try:
        logger.info("=== Starting SIREN Update Check ===")
        log_details.append("===" * 10 + " Starting SIREN Update Check " + 10 * "===")
        log_details.append(f"Started at: {frappe.utils.now()}\n")

        if frappe.cache().get_value('siren_update_running'):
            logger.info("Task already running, exiting")
            log_details.append("Task already running, skipped")
            return "\n".join(log_details)

        try:
            frappe.cache().set_value('siren_update_running', True, expires_in_sec=7200)

            doctypes = [
                {
                    'type': 'Customer',
                    'field_name': 'customer_name',
                    'field_type': 'customer_type',
                    'field_address': 'customer_primary_address',
                    'processed': 0
                },
                {
                    'type': 'Supplier',
                    'field_name': 'supplier_name',
                    'field_type': 'supplier_type',
                    'field_address': 'supplier_primary_address',
                    'processed': 0
                }
            ]

            update = 0
            processed = 0
            errors = 0
            skipped = 0

            for doctype in doctypes:

                log_details.append(f"{'#' * 10} Processing {doctype['type']}s")

                elements = frappe.get_all(
                    doctype['type'],
                    filters=[
                        [doctype['type'], 'siret', '!=', ''],
                    ],
                    or_filters=[
                        [doctype['type'], 'siren', '!=', '']
                    ],
                    fields=[
                        doctype['field_name'],
                        doctype['field_type'],
                        'name',
                        'siren',
                        'siret',
                        'code_naf',
                        'legal_form',
                        'tax_id',
                        doctype['field_address']
                    ],
                )

                log_details.append(f"Found {len(elements)} {doctype['type']} to check\n")

                if len(elements) == 0:
                    log_details.append(f"No {doctype['type']} to process")
                    return "\n".join(log_details)

                for element in elements:
                    try:
                        processed += 1
                        doctype['processed'] += 1

                        # Préparer la requête
                        siret = element.get('siret')
                        siren = element.get('siren')

                        if siret:
                            query_data = {
                                'data': {"siret": siret},
                                'type': "SIRET",
                                'value': siret
                            }
                        elif siren:
                            query_data = {
                                'data': {"siren": siren},
                                'type': "SIREN",
                                'value': siren
                            }
                        else:
                            skipped += 1
                            log_details.append(f"\n{processed}. {element[doctype['field_name']]}")
                            log_details.append(f"Skipped: No SIRET or SIREN")
                            continue

                        log_details.append(f"{processed}. {element[doctype['field_name']]}")
                        log_details.append(f"Calling {query_data['type']}: {query_data['value']}")

                        entity = get_entity(query_data)

                        if entity:
                            logger.info(f"{doctype['type']} {element[doctype['field_name']]} - Data found")
                            log_details.append(f"Data found from API")

                            address = frappe.get_doc('Address', element[doctype['field_address']])

                            if address:
                                compare_values(doctype, element, address.as_dict(), entity)

                                if doctype['processed'] == 1:
                                    mail_body += f"<b><u>{_(doctype['type'])}<u></b><br />"
                                    mail_body += "<table border='0' style='border-bottom:1px solid #eee; width: 100%; margin-bottom:50px;'>"
                                mail_body += "<tr>"
                                mail_body += "<td style='border-bottom:1px solid #eee; padding:6px; font-size:0.833em;'>" + element[doctype['field_name']] + "<a href='#'><img src='" + PICTO_MAGNIFIER + "' style='margin-left:15px; width:20px; height:20px' /></td>"
                                mail_body += "<tr>"

                            else:
                                # TODO : A CONFIRMER SI ON STOP OU SI ON CONTINUE DANS TOUS LES CAS
                                skipped += 1
                                log_details.append(f"No address returned from API")

                        else:
                            skipped += 1
                            log_details.append(f"No data returned from API")

                        log_details.append("\n")


                    except Exception as e:
                        errors += 1
                        error_msg = str(e)
                        logger.error(f"Error processing {element[doctype['field_name']]}: {error_msg}")
                        log_details.append(f"Error: {error_msg}\n")

                        frappe.log_error(
                            message=frappe.get_traceback(),
                            title=f"SIREN API Error: {element.name}"
                        )
                log_details.append("\n" + "=" * 50)
                mail_body += "</table>"

            log_details.append("SUMMARY")
            log_details.append("=" * 50)
            for doctype in doctypes:
                log_details.append(f"Total {doctype['type']}: {doctype['processed']}")
            log_details.append(f"Processed: {processed}")
            log_details.append(f"Skipped: {skipped}")
            log_details.append(f"Errors: {errors}")

            try:
                formated_logs = [detail.replace('\n', '<br />') for detail in log_details]

                frappe.sendmail(
                    recipients=MAIL_TO,
                    subject=MAIL_SUBJECT,
                    message="<div style='padding:10px'>" + mail_body + "</div>",
                    now=True
                )
                logger.info("Rapport envoyé par email")
                log_details.append("\nRapport envoyé par email")
            except Exception as e:
                logger.error(f"Erreur envoi email: {str(e)}")
                log_details.append(f"\nErreur envoi email: {str(e)}")

            log_details.append(f"\nCompleted at: {frappe.utils.now()}")

            logger.info(f"Task completed: {processed} processed, {errors} errors")

        finally:
            frappe.cache().delete_value('siren_update_running')
            log_details.append("\nCache lock released")

        return "\n".join(log_details)

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        log_details.append(f"\n\n❌ FATAL ERROR: {str(e)}")
        log_details.append(f"\n{frappe.get_traceback()}")

        frappe.db.rollback()

        return "\n".join(log_details)


def get_entity(query_data):
    """
    Récupérer les donnees depuis l'API SIRENE
    """
    parameters = frappe.get_doc("ERPNext France Settings")
    if not parameters.api_url:
        logger.error("API URL not configured")
        frappe.log_error("You have to specify an url for SIRENE API")
        return None

    if not parameters.api_token:
        logger.error("API Token not configured")
        frappe.log_error("You have to specify a token for SIRENE API")
        return None

    try:

        url = parameters.api_url + "/siret"
        token = parameters.api_token

        headers = {
            'X-INSEE-Api-Key-Integration': format(token),
            'Accept': 'application/json',
            'Content-Type': "application/x-www-form-urlencoded",
        }

        filters = [query_data['type'].lower()+":"+ query_data['value']]
        response = requests.post(
            url=url,
            data={"q": filters, query_data['type']: query_data['value']},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        return data['etablissements'][0]

    except Timeout:
        logger.error(f"Timeout calling SIRENE API for {query_data['type']} {query_data['value']}")
        return None

    except RequestException as e:
        logger.error(f"Error calling SIRENE API for {query_data['type']} {query_data['value']}: {str(e)}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error for {query_data['type']} {query_data['value']}: {str(e)}")
        return None


def compare_values(doctype, element, address, entity):
    print("#" * 25)
    print(element)
    # print("-" * 25)
    # print(address)

    # print(entity)
    entity_info = get_entity_info(entity)
    print("entity_info :")
    print(entity_info)
    match = True
    match += match and compare_value(element[doctype['field_name']], entity_info['company_name'])
    match += match and compare_value(element[doctype['field_type']], entity_info['entity_type'])
    print("=" * 5)
    print(match)
    #TODO : Finir de faire la logique pour comparer les champs.
    # Reminder :  les champs n'ont pas le meme nom dans entity.
    # + récupérer l'objet doctype dans la fonction pour gestion dyn des champs spéciaux

def compare_value(dval, sval):
    print("||" + sval + " ||||| " + dval + "||")
    match = True
    match = match and (dval == sval)
    return match

def get_entity_info(entity):
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
                elif entityinfo.enseigne3Etablissement not in [None, '[ND]', '']:
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
    vat_intra_calc2 = leftFillNum((12 + 3 * vat_intra_calc) % coef, 2)
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
        "tax_id": tva_intra
    }

    return entity_info

def remove_accents(text):
    """Remove accents from text"""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])

def leftFillNum(num, targetLength) :
    val = str(num)
    return val.rjust(len(val) + targetLength, '0')

