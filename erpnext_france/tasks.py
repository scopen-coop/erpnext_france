


import frappe
from frappe import _

from .controllers.fetch_company_from_sirene import execute_sirene_check


def check_sirene_update():
    """
    Création du Scheduled Job Log
    """
    job_log = create_job_log('check_sirene_update')

    try:
        result = execute_sirene_check()
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



