import frappe
import frappe
from frappe import _
from frappe.utils import cint, flt

import json

from erpnext.controllers.accounts_controller import (
	get_advance_journal_entries,
	get_advance_payment_entries
)

from erpnext.accounts.party import get_party_account

@frappe.whitelist()
def get_down_payment(doc):
	"""Returns list of advances against Account, Party, Reference"""
	doc = json.loads(doc)

	res = get_advance_entries(doc)

	doc['advances'] = []
	advance_allocated = 0
	for d in res:
#		if doc['party_account_currency'] == doc['company_currency']: # sales_invoice.company_currency does not exists
#			amount = doc['base_rounded_total'] or doc['base_grand_total']
#		else:
		amount = doc['rounded_total'] or doc['grand_total']

		allocated_amount = min(amount - advance_allocated, d.amount)
		advance_allocated += flt(allocated_amount)

		advance_row = {
			"doctype": doc['doctype'] + " Advance",
			"reference_type": d.reference_type,
			"reference_name": d.reference_name,
			"reference_row": d.reference_row,
			"remarks": d.remarks,
			"advance_amount": flt(d.amount),
			"allocated_amount": allocated_amount,
			"ref_exchange_rate": flt(d.exchange_rate),  # exchange_rate of advance entry
			"is_down_payment": d.get("down_payment"),
		}

		doc["advances"].append(advance_row)

	return doc


def get_advance_entries(doc, include_unallocated=True):
	party_account = doc['debit_to']
	party_type = "Customer"
	party = doc['customer']
	amount_field = "credit_in_account_currency"
	order_field = "sales_order"
	order_doctype = "Sales Order"

	order_list = list(set(d.get(order_field) for d in doc["items"] if d.get(order_field)))

	journal_entries = get_advance_journal_entries(
		party_type, party, party_account, amount_field, order_doctype, order_list, include_unallocated
	)

	payment_entries = get_advance_payment_entries(
		party_type, party, party_account, order_doctype, order_list, include_unallocated
	)

	res = journal_entries + payment_entries

	if doc['doctype'] == "Sales Invoice" and order_list:
		party_account = get_party_account(party_type, party, doc['company'])
		order_doctype = "Sales Invoice"

		invoice_list = list(
			set(
				frappe.db.sql_list(
					"""
			SELECT si.name
			FROM `tabSales Invoice` si
			LEFT JOIN `tabSales Invoice Item` sii
			ON sii.parent = si.name
			WHERE si.is_down_payment_invoice = 1
			AND sii.sales_order in ({0})
			""".format(
						",".join([f'"{ol}"' for ol in order_list])
					)
				)
			)
		)

		down_payments_je = get_advance_journal_entries(
			party_type,
			party,
			party_account,
			amount_field,
			order_doctype,
			invoice_list,
			include_unallocated,
		)

		down_payments_pe = get_advance_payment_entries(
			party_type, party, party_account, order_doctype, invoice_list, include_unallocated
		)

		res += down_payments_je + down_payments_pe

	return res