# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import requests
import json


@frappe.whitelist()
def fetch_company_from_sirene(data):
	search_values = json.loads(data)
	nb_results = search_values['nb_results']

	parameters = frappe.get_doc('ERPNext France Settings')
	imported_companies = []
	errors = []

	if not parameters.api_url:
		return {'error': _('You have to specify an url for SIRENE API')}

	if not parameters.api_token:
		return {'error': _('You have to specify a token for SIRENE API')}

	filters = get_filters(search_values)
	if not filters:
		return {'error': _('You have to specify at least a filter for searching')}

	try:
		# Init connection with siren
		myToken = parameters.api_token
		myUrl = parameters.api_url + '/siret'

		headers = {
			'Authorization': 'Bearer {}'.format(myToken),
			'Accept': 'application/json',
			'Content-Type': 'application/x-www-form-urlencoded'
		}

		response = http_post(myUrl, headers=headers, data={'q': filters, 'nombre': nb_results})

	except Exception as e:
		return {'error': _('Error during companies data recuperation:{0}').format(e)}

	return {
		'message': response
	}


def http_post(url, headers=None, body=None, data=None):
	try:
		response = requests.post(url=url, json=body, data=data, headers=headers)

		response = json.loads(response.content)
		if response['header']['statut'] not in [201, 200]:
			if response['header']['statut'] == 401:
				frappe.db.commit()
				frappe.throw(response["message"], title=_("SIRENE Error - Unauthorized"))
			elif response['header']['statut'] == 403:
				frappe.msgprint(_("You didn't have permission to access this API"))
				frappe.throw(response["message"], title=_("SIRENE Error - Access Denied"))
			elif response['header']['statut'] == 404:
				frappe.throw(response['header']["message"], title=_("SIRENE Error - Not Found"))
			else:
				frappe.throw(response['header']['reason'], title=response['header']['statut'])

	except Exception as e:
		frappe.throw(str(e))

	return response


def get_filters(search_values):
	filters = []
	if 'company_name' in search_values and search_values['company_name'] != '':
		filters.append('raisonSociale:"' + search_values['company_name'].replace('"', '\\"') + '"')

	if 'siren' in search_values and search_values['siren'] != '':
		filters.append('siren:' + search_values['siren'])

	if 'siret' in search_values and search_values['siret'] != '':
		filters.append('siret:' + search_values['siret'])

	if 'naf' in search_values and search_values['naf'] != '':
		filters.append('activitePrincipaleUniteLegale:' + search_values['naf'])

	if 'zipcode' in search_values and search_values['zipcode'] != '':
		filters.append('codePostalEtablissement:' + search_values['zipcode'])

	filters.append('-periode(etatAdministratifEtablissement:F)')

	return ' AND '.join(filters)
