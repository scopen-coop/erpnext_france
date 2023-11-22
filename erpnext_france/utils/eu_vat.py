# -*- coding: utf-8 -*-
# Copyright (c) 2023 SCOPEN
# For license information, please see license.txt

import frappe
from frappe import _

import re
from zeep import Client

WSDL_URL = "https://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl"
COUNTRY_CODE_REGEX = r"^[A-Z]{2}$"
VAT_NUMBER_REGEX = r"^[0-9A-Za-z\+\*\.]{2,12}$"


@frappe.whitelist(allow_guest=False)
def check_vat(vat_id: str):
	country_code = vat_id[:2].upper()
	vat_number = vat_id[2:].replace(" ", "")

	# check vat_number and country_code with regex
	if not re.match(COUNTRY_CODE_REGEX, country_code):
		frappe.throw(_("Invalid country code"))

	if not re.match(VAT_NUMBER_REGEX, vat_number):
		frappe.throw(_("Invalid VAT number"))

	return check_vat_ws(country_code, vat_number)


def check_vat_ws(country_code: str, vat_number: str):
	"""Use the EU VAT checker to validate a VAT ID."""
	res = {}
	res['valid']=False
	res['countryCode']=''
	res['vatNumber']=''
	res['name']=''
	res['address']=''

	try:
		res = Client(WSDL_URL).service.checkVat(
			vatNumber=vat_number, countryCode=country_code
		)
	except Exception as e:
		if (str(e)=='INVALID_INPUT'):
			frappe.throw(_('Invalid VAT number'))

	return {
		"valid":res['valid'],
		"countryCode":res['countryCode'],
		"vatNumber":res['vatNumber'],
		"name":res['name'],
		"address":res['address'],
	}
