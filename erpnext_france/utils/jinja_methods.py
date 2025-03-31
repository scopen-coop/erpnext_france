import math
import re

import frappe

# from erpnext.setup.doctype.company.company import get_default_company_address
from frappe import _
from frappe.contacts.doctype.address.address import get_default_address
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe.utils import cint
from frappe.utils.data import format_date


def build_ecopart_table(doc):
	if len(doc.items) == 0:
		return "<b>" + _("No Line In This Document") + "</b>"

	html = f"""
        <table class="table borderless table-condensed " >
            <tr class="" >
                <th class="verdana">{_("Designation")}</th>
                <th class="col_price verdana">{_("Total")}</th>
            </tr>
        """

	tax_map = get_tax_map(doc)
	for tax_account in tax_map.keys():
		if tax_map[tax_account]["type"] != "Actual":
			continue

		html += f"""
            <tr class="line_bordered">
                <td class="verdana taxes">{_("Ecopart Total")}</td>
                <td class="verdana right">
                    {frappe.format_value(tax_map[tax_account]['amount'], {"fieldtype": "Currency"})}
                </td>
            </tr>
        """

	for tax_account in tax_map.keys():
		if tax_map[tax_account]["type"] == "Actual":
			continue

		html += f"""
            <tr class="line_bordered">
                <td class="verdana taxes">
                    {_("TVA {0} %").format(str(round(tax_map[tax_account]['tax_rate'], 2)))}
                </td>
                <td class="verdana right">
                    {frappe.format_value(tax_map[tax_account]['amount'], {"fieldtype": "Currency"})}
                </td>
            </tr>
        """

	html += f"""
		<tr class="total line_bordered">
			<td class="verdana total">Total TTC</td>
			<td class="verdana total right">{frappe.format_value(doc.grand_total, {"fieldtype": "Currency"})}</td>
        </tr>
    """

	html += """</table>"""

	return html


def get_tax_map(doc):
	tax_map = {}
	for tax in doc.taxes:
		if tax.tax_amount == 0:
			continue

		account = frappe.get_doc("Account", tax.account_head)
		if tax.account_head not in tax_map:
			tax_map[tax.account_head] = {
				"tax_rate": account.tax_rate,
				"amount": tax.tax_amount,
				"type": tax.charge_type,
			}

		tax_map[tax.account_head]["amount"] += tax.tax_amount
	return tax_map
