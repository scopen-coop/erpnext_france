import frappe
from frappe import _

from .controllers.fetch_company_from_sirene import execute_sirene_check, send_sirene_report

SITE_URL = frappe.utils.get_url() + "/app"
MAIL_SUBJECT = _("SIRENE - Updates available")
MAIL_TO_CUSTOMER = [frappe.get_doc("ERPNext France Settings").customer_recovery_email]
MAIL_TO_SUPPLIER = [frappe.get_doc("ERPNext France Settings").supplier_recovery_email]
MAIL_BODY_HEADER = _("Updates available for the entities below:")


def check_sirene_update():
	"""
	Création du Scheduled Job Log
	"""
	job_log = create_job_log("check_sirene_update")

	try:
		results = execute_sirene_check()
		total_updates = sum(len(updates) for updates in results["updates"].values())

		if total_updates > 0 or results["errors_customer"] > 0:
			send_sirene_report(
				results=results,
				recipients_customer=MAIL_TO_CUSTOMER,
				recipients_supplier=MAIL_TO_SUPPLIER,
				site_url=SITE_URL,
				subject=MAIL_SUBJECT,
			)

		log_message = "\n".join(results["logs"])

		complete_job_log(job_log, status="Complete", details=log_message)
		print("Task successfully completed")

	except Exception as e:
		error_details = f"Fatal Error: {e!s}\n\n{frappe.get_traceback()}"
		complete_job_log(job_log, status="Failed", details=error_details)

		frappe.log_error(frappe.get_traceback(), "SIREN Update Check - Task Failed")
		print("SIREN Update Check - Task Failed")


def create_job_log(method_name):
	"""
	Créer un Scheduled Job Log
	"""

	job_type_name = frappe.db.get_value(
		"Scheduled Job Type", {"method": f"erpnext_france.tasks.{method_name}"}, "name"
	)

	if not job_type_name:
		job_type = frappe.get_doc(
			{
				"doctype": "Scheduled Job Type",
				"method": f"erpnext_france.tasks.{method_name}",
				"frequency": "Daily",
			}
		)
		job_type.insert(ignore_permissions=True)
		frappe.db.commit()
		job_type_name = job_type.name

	job_log = frappe.get_doc(
		{
			"doctype": "Scheduled Job Log",
			"scheduled_job_type": job_type_name,
			"status": "Scheduled",
			"details": f"Started at {frappe.utils.now()}",
		}
	)
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
