# -*- coding: utf-8 -*-
# Copyright (c) 2024 SCOPEN
# For license information, please see license.txt


import frappe
from erpnext.setup.doctype.company.company import Company
from frappe import _


@frappe.whitelist(allow_guest=False)
def create_tax_template(doc: Company):
    if not frappe.db.exists("Company", doc.company_name):
        frappe.throw(
            _("Company {} does not exist yet. Taxes setup aborted.").format(
                doc.company_name
            )
        )

    # file_path = os.path.join(
    #     os.path.dirname(__file__), "..", "data", "country_wise_tax.json"
    # )
    # with open(file_path) as json_file:
    #     tax_data = json.load(json_file)

    # country_wise_tax = tax_data.get(doc.country)

    # if not country_wise_tax:
    #     return
    #
    # if "chart_of_accounts" not in country_wise_tax:
    #     country_wise_tax = simple_to_detailed(country_wise_tax)
    #
    # from_detailed_data(company_name, country_wise_tax)
    # update_regional_tax_settings(country, company_name)
