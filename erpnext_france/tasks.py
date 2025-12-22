import frappe
import requests
from requests.exceptions import RequestException, Timeout
logger = frappe.logger("scheduler")
logger.setLevel("INFO")

def check_sirene_update():
    try:
        logger.info("=== Starting SIREN Update Check ===")

        if frappe.cache().get_value('siren_update_running'):
            logger.info("Task already running, exiting")
            return None


        frappe.cache().set_value('siren_update_running', True, expires_in_sec=7200)

        logger.info("# Processing customers")

        customers = frappe.get_all(
            'Customer',
            fields=['name', 'siren', 'siret', 'customer_name'],
        )
        logger.info(f"{len(customers)} customers to check")

        for customer in customers:
            try:
                query_data = {}
                siret = customer.siret
                siren = customer.siren

                if siret:
                    #data = {"siret": siret}
                    query_data =  {
                        'data': {"siret": siret},
                        'type': "SIRET",
                        'value': siret
                    }
                elif siren:
                    #data = {"siren": siren}
                    query_data =  {
                        'data': {"siren": siren},
                        'type': "SIREN",
                        'value': siren
                    }
                else:
                    frappe.throw("SIRET or SIREN must be specified to retrieve a third party")


                entity = get_entity(query_data)

                if entity:
                    logger.info(f"Customer Found")

            except Exception as e:
                frappe.log_error(
                    message=frappe.get_traceback(),
                    title=f"SIREN API Error: {customer.name}"
                )


    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "SIREN Task Failed")
        frappe.db.rollback()
    finally:
        frappe.cache().delete_value('siren_update_running')


def get_entity(query_data):
    """
    Récupérer les données depuis l'API SIRENE
    """
    parameters = frappe.get_doc("ERPNext France Settings")

    if not parameters.api_url:
        frappe.log_error("You have to specify an url for SIRENE API")
        return None

    if not parameters.api_token:
        frappe.log_error("error : You have to specify a token for SIRENE API")
        return None
    try:
        logger.info(f"Calling {query_data['type']} {query_data['value']}")
        url = parameters.api_url + "/siret"
        token = parameters.api_token

        headers = {
            'X-INSEE-Api-Key-Integration': format(token),
            'Accept': 'application/json',
            'Content-Type': "application/x-www-form-urlencoded",
        }

        response = requests.post(url=url, data=query_data['data'], headers=headers)


        response.raise_for_status()

        # Parser le JSON
        data = response.json()

        logger.info(f"SIRENE API response for {query_data['type']} {query_data['value']}: {response.status_code}")

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
