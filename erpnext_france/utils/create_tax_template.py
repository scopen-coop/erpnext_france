# -*- coding: utf-8 -*-
# Copyright (c) 2024 SCOPEN
# For license information, please see license.txt


import json
import os

import frappe
from erpnext.setup.setup_wizard.operations.taxes_setup import (
    from_detailed_data,
    update_regional_tax_settings,
)
from frappe import _


@frappe.whitelist(allow_guest=False)
def create_tax_template(doc: str):
    doc = json.loads(doc)

    company_name = doc.get("company_name")
    country = doc.get("country")
    if not frappe.db.exists("Company", company_name):
        frappe.throw(
            _("Company {} does not exist yet. Taxes setup aborted.").format(
                company_name
            )
        )

    file_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "country_wise_tax.json"
    )
    with open(file_path) as json_file:
        tax_data = json.load(json_file)

    country_wise_tax = tax_data.get(country)

    if not country_wise_tax:
        return

    from_detailed_data(company_name, country_wise_tax)
    update_regional_tax_settings(country, company_name)
