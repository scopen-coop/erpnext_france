import json
import time


import frappe
from frappe import _

from .controllers.fetch_company_from_sirene import fetch_company_from_sirene, compare_values

logger = frappe.logger("scheduler")
logger.setLevel("INFO")

frappe.local.lang = "fr"
SITE_URL = frappe.utils.get_site_url(frappe.local.site) + "/app"
MAIL_SUBJECT = _("SIRENE - Updates available")
PICTO_SHOW = "https://cdn.iconscout.com/icon/free/png-256/free-magnifying-glass-icon-svg-download-png-1798586.png"
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
        print("Task successfully completed")

    except Exception as e:
        error_details = f"Fatal Error: {str(e)}\n\n{frappe.get_traceback()}"
        complete_job_log(job_log, status='Failed', details=error_details)

        frappe.log_error(frappe.get_traceback(), "SIREN Update Check - Task Failed")
        print("SIREN Update Check - Task Failed")


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
    mail_body = "<h4>ERPNext France</h4>"
    mail_body += "<p>" + MAIL_BODY_HEADER + "</p>"
    log_details = []

    try:
        logger.info("=== Starting SIREN Update Check ===")
        print("=== Starting SIREN Update Check ===")
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
                    'processed': 0,
                    'update': 0
                },
                {
                    'type': 'Supplier',
                    'field_name': 'supplier_name',
                    'field_type': 'supplier_type',
                    'field_address': 'supplier_primary_address',
                    'processed': 0,
                    'update': 0
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

                        data_to_post = {
                            query_data['type'].lower(): query_data['value'],
                            "nb_results": 1,
                        }

                        response = fetch_company_from_sirene(json.dumps(data_to_post))
                        entity = response['message']['etablissements'][0]

                        # Add a sleep each 50 ajax calls to prevent api flooding
                        if processed % 25 == 0:
                            print("Pause")
                            time.sleep(5)

                        if entity:
                            logger.info(f"{doctype['type']} {element[doctype['field_name']]} - Data found")
                            log_details.append(f"Data found from API")

                            address = frappe.get_doc('Address', element[doctype['field_address']])

                            if address:
                                match = compare_values(doctype, element, address.as_dict(), entity)

                                if not match:
                                    if doctype['update'] == 0:
                                        mail_body += f"<b><u>{_(doctype['type'])}(s)<u></b><br />"
                                        mail_body += "<table border='0' style='border-bottom:1px solid #eee; width: 100%; margin-bottom:50px;'>"
                                    mail_body += "<tr>"
                                    mail_body += "<td style='border-bottom:1px solid #eee; padding:6px; font-size:0.833em;'>" + element[doctype['field_name']] + "<a href='" + SITE_URL + "/" + doctype['type'].lower() + "/" + element['name'] + "' style='padding-left:10px;'>" + _("View") + " ↗</a><td>"
                                    mail_body += "<tr>"

                                    doctype['update'] += 1

                            else:
                                # TODO : A CONFIRMER SI ON STOP OU SI ON CONTINUE DANS TOUS LES CAS
                                skipped += 1
                                log_details.append(f"No address returned from ErpNext API")

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








