# -*- coding: utf-8 -*-
# Copyright (c) 2021, scopen.fr and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from erpnext.accounts.general_ledger import flt, make_entry


def correct_gl_entry_supplier_discount(doc, method):
    if doc is not None and doc.discount_amount != 0:
        discount_account = frappe.get_cached_value('Company', doc.company, "discount_supplier_account")
        if discount_account is not None:

            precision = frappe.get_precision("GL Entry", "debit_in_account_currency")

            # Build Item accountancy code dict to know what line update into GL Entry
            item_code_and_net = {}
            for docline in doc.items:
                if docline.expense_account in item_code_and_net:
                    item_code_and_net[docline.expense_account] += flt(docline.amount)
                else:
                    item_code_and_net[docline.expense_account] = flt(docline.amount)

            gl_invoice_entries = frappe.get_list("GL Entry",
                                                 filters={'voucher_no': doc.name, 'voucher_type': doc.doctype})
            if gl_invoice_entries is not None and len(gl_invoice_entries) != 0:
                for gl_invoice_entry in gl_invoice_entries:
                    gl_entry = frappe.get_doc('GL Entry', gl_invoice_entry.name)
                    if gl_entry.party_type == "Supplier":
                        gl_entry.db_set('credit', doc.net_total)
                        gl_entry.db_set('credit_in_account_currency', doc.net_total)
                    elif gl_entry.account in item_code_and_net.keys():
                        gl_entry.db_set('debit', item_code_and_net[gl_entry.account])
                        gl_entry.db_set('debit_in_account_currency', item_code_and_net[gl_entry.account])

            new_gl_entry = doc.get_gl_dict({
                "account": discount_account,
                "against": doc.supplier_name,
                "cost_center": doc.get_company_default("cost_center"),
                "project": doc.get("project"),
                "remarks": "Supplier Discount",
                "credit": flt(doc.discount_amount, precision),
                "is_opening": "No"
            })
            make_entry(new_gl_entry, adv_adj=False, update_outstanding='No')
