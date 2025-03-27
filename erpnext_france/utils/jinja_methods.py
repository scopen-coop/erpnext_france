import math
import re

import frappe

# from erpnext.setup.doctype.company.company import get_default_company_address
from frappe import _
from frappe.contacts.doctype.address.address import get_default_address
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe.utils import cint
from frappe.utils.data import format_date

def print_standard_document(doc):
    return f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100..900;1,100..900&display=swap');
        </style>
        {print_first_page(doc)}
        {build_items_table(doc)}
        <div class="page-break"></div>
        {print_last_page(doc)}
    """


def letter_head_by_doctype(doc):
    company = frappe.get_doc("Company", doc.company)
    logo_html = ""
    if company.company_logo:
        logo_html = (
            '<img src="' + str(company.company_logo) + '" style="width: 150px;">'
        )

    return f"""
        <div id="header-html" class="roboto container letter-head page-header hidden-pdf">
            <div class="row">
                <div class="column-break col-xs-6">
                    {logo_html}
                </div>
                <div class="roboto column-break col-xs-6 text-right">
                    <div class="roboto site">
                        {str(company.website)}
                    </div>
                    <br>
                    {_(str(doc.doctype) + ' Number')}: {str(doc.name)}
                </div>
            </div>
        </div>
    """


def footer_by_doctype(doc):
    company = frappe.get_doc("Company", doc.company)
    address = {}
    if get_default_address("Company", company.name):
        address = frappe.get_doc("Address", get_default_address("Company", company.name))


    address_html = ""
    if address:
        address_html = format_address(address, "-")

    phone_no = ""
    if company.phone_no:
        phone_no = " - " + str(company.phone_no)
    fax_no = ""
    if company.fax:
        fax_no = " - fax " + str(company.fax)

    email = ""
    if company.email:
        email = " - " + str(company.email)

    legal_form = ""
    if company.legal_form:
        form = frappe.get_doc("Legal Form", company.legal_form)
        legal_form = str(form.label)

    html = f"""
        <div id="footer-html" style="height: 50px; position: fixed; bottom 0;" class="roboto">
            <div class="green-rectangle">
                <div class="roboto first-line">
                    <b>{str(company.abbr)}</b> - {address_html}{phone_no}{fax_no}{email}
                </div>
                <div class="roboto second-line">
                    {legal_form} - SIRET {str(company.siret)} - N° TVA {str(company.tax_id)} - APE {str(company.code_naf)}
                </div>
            </div>
            <p class="roboto text-center small page-number visible-pdf">
               {_("Page {0} of {1}").format('<span class="page"></span>', '<span class="topage"></span>')}
            </p>
        </div>
    """

    return html


def format_address(address, separator):
    address_html = ""
    if address.get('address_line1'):
        address_html += str(address.get('address_line1'))
    if address.get('address_line2'):
        address_html += separator + str(address.get('address_line2'))
    if address.get('pincode'):
        address_html += separator + str(address.get('pincode'))
    if address.get('city'):
        address_html += separator + str(address.get('city'))
    if address.get('state'):
        address_html += separator + str(address.get('state'))
    return address_html


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


def build_items_table(doc):
    if len(doc.items) == 0:
        return "<b>" + _("No Line In This Document") + "</b>"

    html = f"""
        <table class="table borderless table-condensed " >
            <tr class="" >
                <th class="verdana">{_("Designation")}</th>
                <th class="verdana">{_("Unit")}</th>
                <th class="verdana">{_("Qty")}</th>
                <th class="col_price verdana">{_("Unit Price")}</th>
                <th class="col_price verdana">{_("Total")}</th>
                <th class="verdana">{_("TVA Tx")}</th>
            </tr>
        """

    for item in doc.items:
        tva = 0
        if item.item_tax_template:
            taxe = frappe.get_doc("Item Tax Template", item.item_tax_template)
            if taxe.get("taxes") and len(taxe.taxes) > 0:
                tva = taxe.taxes[0].get("tax_rate") or 0

        html += f"""
            <tr class="item">
                <td class="verdana item pl-2">{str(item.description)}</td>
                <td class="verdana item">{str(item.uom)}</td>
                <td class="verdana item">{str(item.qty)}</td>
                <td class="verdana item right">{frappe.format_value(item.rate, {"fieldtype": "Currency"})}</td>
                <td class="verdana item right">{frappe.format_value(item.amount, {"fieldtype": "Currency"})}</td>
                <td class="verdana item right">{frappe.format_value(tva, {"fieldtype": "Percent"})}</td>
            </tr>
        """

    html += f"""
		<tr class="total line_bordered">
			<td class="total">Total HT</td>
			<td></td>
			<td></td>
			<td></td>
			<td class="verdana total right">{frappe.format_value(doc.total, {"fieldtype": "Currency"})}</td>
	        <td></td>
	    </tr>
    """

    tax_map = get_tax_map(doc)

    for tax_account in tax_map.keys():
        if tax_map[tax_account]["type"] != "Actual":
            continue

        html += f"""
            <tr class="line_bordered">
                <td class="verdana taxes">{_("Ecopart Total")}</td>
                <td></td>
                <td></td>
                <td></td>
                <td class="verdana right">
                    {frappe.format_value(tax_map[tax_account]['amount'], {"fieldtype": "Currency"})}
                </td>
                <td></td>
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
                <td></td>
                <td></td>
                <td></td>
                <td class="verdana right">
                    {frappe.format_value(tax_map[tax_account]['amount'], {"fieldtype": "Currency"})}
                </td>
                <td></td>
            </tr>
        """

    html += f"""
		<tr class="total line_bordered">
			<td class="verdana total">Total TTC</td>
			<td></td>
			<td></td>
			<td></td>
			<td class="verdana total right">{frappe.format_value(doc.grand_total, {"fieldtype": "Currency"})}</td>
            <td></td>
        </tr>
    """

    html += """</table>"""

    if doc.doctype == "Sales Invoice":
        html += print_net_amount(doc)

    return html


def print_net_amount(doc):
    html = f"""
        <div class="row">
            <div class="col col-xs-8"></div>
            <div class="col column-break col-xs-4 green-rectangle verdana address customer-address">
                <b>{_('Net Amount TTC') + '&nbsp' + frappe.format_value(doc.grand_total, {"fieldtype": "Currency"})}</b>
            </div>
        </div>"""
    return html




def print_first_page(doc):
    company = frappe.get_doc("Company", doc.company)
    address = {}
    if get_default_address("Company", company.name):
        address = frappe.get_doc("Address", get_default_address("Company", company.name))

    html = f"""
        {print_customer_address(doc)}
        {print_doc_information(doc)}
        <br/><br/>
        <div class="verdana right">{str(address.get('city'))}, {format_date(doc.transaction_date, 'dd/mm/YY')}</div>
    """

    if not doc.get("front_page"):
        return html

    html += f"""
        <br/><br/>
        <div class="verdana m-10">
            {print_front_page_text(doc)}
        </div>
        <div class="page-break"></div>
    """
    return html


def print_front_page_text(doc):
    return doc.text_front_page.replace("\n", "<br>\n") if doc.text_front_page else ""


def print_last_page(doc):
    html = f"""
        {print_customer_address(doc)}
        {print_doc_information(doc)}
        """

    if doc.doctype == "Quotation":
        html += f"""
            <div class="verdana row p-3">
                {_(doc.doctype + " Conditions Text")}
            </div>
            """

    html += f"""
        <table class="recap_amounts">
            <tr>
                <td style="width : 20% ;">{_("Amount HT")}</td>
                <td style="width : 20% ;" class="verdana right price"><b>{frappe.format_value(doc.total, {"fieldtype": "Currency"})}</b></td>
            <tr>
        """

    tax_map = get_tax_map(doc)

    for tax_account in tax_map.keys():
        if tax_map[tax_account]["type"] != "Actual":
            continue

        html += f"""
            <tr>
                <td style="width : 20% ;" class="verdana">{_("Ecopart Total")}</td>
                <td style="width : 20% ;" class="verdana right price">
                    {frappe.format_value(tax_map[tax_account]['amount'], {"fieldtype": "Currency"})}
                </td>
            </tr>
        """

    for tax_account in tax_map.keys():
        if tax_map[tax_account]["type"] == "Actual":
            continue

        html += f"""
            <tr>
                <td style="width : 20% ;" class="verdana">
                    {_("TVA {0} %").format(str(round(tax_map[tax_account]['tax_rate'], 2)))}
                </td>
                <td style="width : 20% ;" class="verdana right price">
                    {frappe.format_value(tax_map[tax_account]['amount'], {"fieldtype": "Currency"})}
                </td>
            </tr>
        """

    html += f"""
    		<tr>
    			<td style="width : 20% ;" class="verdana"><b>Total TTC</b></td>
    			<td style="width : 20% ;" class="verdana right price"><b>{frappe.format_value(doc.grand_total, {"fieldtype": "Currency"})}</b></td>
            </tr>
        </table>
        <div class="row p-3">
            <i class="verdana">{frappe.utils.money_in_words(doc.grand_total)}</i>
        </div>
        """

    if doc.doctype == "Quotation":
        html += f"""
            <div class="verdana row p-3">
                {_(doc.doctype + " Conditions Date Text")}
            </div>
            <div class="center"><b class="verdana">{_('Acceptation')}</b></div>
            <br>
            <div class="verdana insurance_text">
                {_('Acceptation Date')}
            </div>
            <br>
            <div class="verdana right">{str(doc.customer_name)}</div>
            <br>
            <div class="verdana signature right"><i>{_('Signature Mention')}</i></div>
        """

    return html


def print_customer_address(doc):
    customer_address = None
    if doc.customer_address:
        customer_address = frappe.get_doc(
            "Address", doc.customer_address, as_dict="True"
        )

    address_html = ""
    if customer_address:
        address_html = format_address(customer_address, "<br>")

    customer = frappe.get_doc("Customer", doc.customer_name)
    if customer.get("customer_type") == "Individual":
        contact_name = get_default_contact("Customer", doc.customer_name)
        if contact_name:
            contact = frappe.get_doc("Contact", contact_name)
            civility = (
                str(contact.salutation) + " " if contact.salutation is not None else ""
            )
            name_and_civility = str(civility) + str(contact.full_name)
        else:
            name_and_civility = str(customer.name)
    else:
        name_and_civility = str(customer.name)

    return f"""
        <div class="text-right">
            <div class="verdana address customer-address">
                <b>{name_and_civility}</b><br/>
                {address_html} <br/>
            </div>
        </div>
    """

def print_doc_information(doc):
    validity_period = ""
    if doc.get("valid_till") is not None:
        validity_period = (
            _(doc.doctype + " Validity Period")
            + " : <b>"
            + format_date(doc.valid_till, "dd/mm/YY")
            + "</b>"
        )

    quotation_subject = ""
    if doc.get("quotation_subject") is not None:
        quotation_subject = _("Object") + " : " + str(doc.quotation_subject)

    visiting_date = ""
    if doc.get("visiting_date") is not None:
        visiting_date = (
            "<b>"
            + (
                _("Visiting Date")
                + " : "
                + format_date(doc.visiting_date, "dd/mm/YY")
            )
            + "</b>"
        )

    return f"""
        <div class="row">
            <div class="verdana column-break col-xs-6 text-left">
                {validity_period}
            </div>
        </div>
        <br>
        <div class="verdana">
            {quotation_subject}<br/>
            {visiting_date}
        </div>
        <br>
    """

