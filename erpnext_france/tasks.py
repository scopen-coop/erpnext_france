import frappe
import requests
from requests.exceptions import RequestException, Timeout
logger = frappe.logger("scheduler")
logger.setLevel("INFO")


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

    job_type_name = frappe.db.get_value('Scheduled Job Type',
                                        {'method': f'erpnext_france.tasks.{method_name}'},
                                        'name')

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
    log_details = []

    try:
        logger.info("=== Starting SIREN Update Check ===")
        log_details.append("===" * 10 +  " Starting SIREN Update Check " + 10 *  "===")
        log_details.append(f"Started at: {frappe.utils.now()}\n")

        if frappe.cache().get_value('siren_update_running'):
            logger.info("Task already running, exiting")
            log_details.append("Task already running, skipped")
            return "\n".join(log_details)

        try:
            frappe.cache().set_value('siren_update_running', True, expires_in_sec=7200)

            doctypes = [
                {
                    'type' : 'Customer',
                    'field_name' : 'customer_name',
                    'processed' : 0
                },
                {
                    'type' : 'Supplier',
                    'field_name' : 'supplier_name',
                    'processed': 0
                }
            ]

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
                    fields=['name', 'siren', 'siret', doctype['field_name']],
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

            log_details.append("SUMMARY")
            log_details.append("=" * 50)
            for doctype in doctypes:
                log_details.append(f"Total {doctype['type']}: {doctype['processed']}")
            log_details.append(f"Processed: {processed}")
            log_details.append(f"Skipped: {skipped}")
            log_details.append(f"Errors: {errors}")
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

        response = requests.post(
            url=url,
            data=query_data['data'],
            headers=headers,
            timeout=10  # Timeout de 10 secondes
        )

        response.raise_for_status()

        data = response.json()

        return data

    except Timeout:
        logger.error(f"Timeout calling SIRENE API for {query_data['type']} {query_data['value']}")
        return None

    except RequestException as e:
        logger.error(f"Error calling SIRENE API for {query_data['type']} {query_data['value']}: {str(e)}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error for {query_data['type']} {query_data['value']}: {str(e)}")
        return None
