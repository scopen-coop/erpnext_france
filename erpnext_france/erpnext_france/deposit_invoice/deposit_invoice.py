# -*- coding: utf-8 -*-
# Copyright (c) 2021, Britlog and Contributors
# Copyright (c) 2023 SCOPEN
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.utils import get_fetch_values
from frappe.model.mapper import get_mapped_doc
from frappe.contacts.doctype.address.address import get_company_address


@frappe.whitelist()
def get_payment_schedule_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select payment_term
		from `tabPayment Schedule`
		where parent = '{0}' and payment_term IS NOT NULL
		""".format(filters.get("parent")))


@frappe.whitelist()
def make_deposit_invoice(source_name, target_doc=None, ignore_permissions=False):
    def postprocess(source, target):
        set_missing_values(source, target)
        # Get the advance paid Journal Entries in Sales Invoice Advance
        if target.get("allocate_advances_automatically"):
            target.set_advances()

    def set_missing_values(source, target):
        target.ignore_pricing_rule = 1
        target.flags.ignore_permissions = True
        target.run_method("set_missing_values")
        target.run_method("set_po_nos")
        target.run_method("calculate_taxes_and_totals")

        if source.company_address:
            target.update({'company_address': source.company_address})
        else:
            # set company address
            target.update(get_company_address(target.company))

        if target.company_address:
            target.update(get_fetch_values("Sales Invoice", 'company_address', target.company_address))

        # set print heading
        target.select_print_heading = frappe.db.get_single_value('ERPNext France Settings', 'deposit_print_heading')

    def update_item(source, target, source_parent):

        if frappe.flags.args and frappe.flags.args.payment_term:
            for term in source_parent.payment_schedule:
                if frappe.flags.args.payment_term == term.payment_term:
                    invoice_portion = term.invoice_portion
                    target.qty = source.qty * (invoice_portion / 100)
                    target.description = source.description \
                                         + "<br>Acompte de {0} % sur la commande n° {1}".format(invoice_portion,
                                                                                                source_parent.name)

    doclist = get_mapped_doc("Sales Order", source_name, {
        "Sales Order": {
            "doctype": "Sales Invoice",
            "field_map": {
                "party_account_currency": "party_account_currency"
            },
            "validation": {
                "docstatus": ["=", 1]
            }
        },
        "Sales Order Item": {
            "doctype": "Sales Invoice Item",
            "field_map": {
                "name": "so_detail",
                "parent": "sales_order",
            },
            "postprocess": update_item
        },
        "Sales Taxes and Charges": {
            "doctype": "Sales Taxes and Charges",
            "add_if_empty": True
        },
        "Sales Team": {
            "doctype": "Sales Team",
            "add_if_empty": True
        }
    }, target_doc, postprocess, ignore_permissions=ignore_permissions)

    return doclist
