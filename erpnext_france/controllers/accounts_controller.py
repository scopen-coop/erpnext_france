# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import frappe
import frappe
from frappe import _
from frappe.utils import cint, flt, fmt_money
from frappe.query_builder.functions import Abs, Sum
from frappe.query_builder.custom import ConstantColumn

import json

from erpnext.controllers.accounts_controller import get_advance_journal_entries
from erpnext.accounts.party import get_party_account
from erpnext.accounts.utils import reconcile_against_document


@frappe.whitelist()
def get_down_payment(doc):
	"""Returns list of advances against Account, Party, Reference"""
	doc = json.loads(doc)

	res = get_advance_entries(doc)

	doc['advances'] = []
	advance_allocated = 0
	for d in res:
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


def get_advance_entries(doc):
	party_type = "Customer"
	party = doc['customer']
	amount_field = "credit_in_account_currency"
	order_field = "sales_order"
	order_doctype = "Sales Order"

	party_account = get_party_account(
		party_type, party=party, company=doc['company'], include_advance=True
	)

	order_list = list(set(d.get(order_field) for d in doc["items"] if d.get(order_field)))

	journal_entries = get_advance_journal_entries(
		party_type, party, party_account, amount_field, order_doctype, order_list, False
	)

	payment_entries = get_advance_payment_entries(
		party_type, party, party_account, order_doctype, order_list
	)

	res = journal_entries + payment_entries

	if doc['doctype'] == "Sales Invoice" and order_list:
		party_account = [get_party_account(party_type, party, doc['company'])]
		invoice_doctype = "Sales Invoice"

		si = frappe.qb.DocType("Sales Invoice")
		sii = frappe.qb.DocType("Sales Invoice Item")
		old_invoice_list = (
			frappe.qb.from_(si)
			.left_join(sii)
			.on(sii.parent == si.name)
			.select(si.name)
			.where(si.is_down_payment_invoice == 1)
			.where(sii.sales_order.isin(order_list))
			.run(as_list=True)
		)

		invoice_list = [invoice[0] for invoice in old_invoice_list]

		down_payments_je = get_advance_journal_entries(
			party_type,
			party,
			party_account,
			amount_field,
			invoice_doctype,
			invoice_list,
			False,
		)

		down_payments_pe = get_advance_payment_entries(
			party_type, party, party_account, invoice_doctype, invoice_list
		)

		res += down_payments_je + down_payments_pe

	return res


def update_against_document_in_jv(doc):
	"""
	Links invoice and advance voucher:
			1. cancel advance voucher
			2. split into multiple rows if partially adjusted, assign against voucher
			3. submit advance voucher
	"""
	if doc.doctype == "Sales Invoice":
		party_type = "Customer"
		party = doc.customer
		party_account = doc.debit_to
		dr_or_cr = "credit_in_account_currency"
	else:
		party_type = "Supplier"
		party = doc.supplier
		party_account = doc.credit_to
		dr_or_cr = "debit_in_account_currency"

	lst = []

	for d in doc.get("advances"):
		if flt(d.allocated_amount) <= 0:
			continue

		down_payment = (
			cint(frappe.db.get_value(d.reference_type, d.reference_name, "down_payment"))
			if d.reference_type == "Payment Entry"
			else 0
		)

		if down_payment:
			continue

		args = frappe._dict(
			{
				"voucher_type": d.reference_type,
				"voucher_no": d.reference_name,
				"voucher_detail_no": d.reference_row,
				"against_voucher_type": doc.doctype,
				"against_voucher": doc.name,
				"account": party_account,
				"party_type": party_type,
				"party": party,
				"is_advance": "Yes",
				"dr_or_cr": dr_or_cr,
				"unadjusted_amount": flt(d.advance_amount),
				"allocated_amount": flt(d.allocated_amount),
				"precision": d.precision("advance_amount"),
				"exchange_rate": (
					doc.conversion_rate if doc.party_account_currency != doc.company_currency else 1
				),
				"grand_total": (
					doc.base_grand_total
					if doc.party_account_currency == doc.company_currency
					else doc.grand_total
				),
				"outstanding_amount": doc.outstanding_amount,
				"difference_account": frappe.get_cached_value(
					"Company", doc.company, "exchange_gain_loss_account"
				),
				"exchange_gain_loss": flt(d.get("exchange_gain_loss")),
			}
		)
		lst.append(args)
	if lst:
		from erpnext.accounts.utils import reconcile_against_document

		reconcile_against_document(lst)


def set_total_advance_paid(doc):
	ple = frappe.qb.DocType("Payment Ledger Entry")
	party = doc.customer if doc.doctype == "Sales Order" else doc.supplier
	advance_query = (
		frappe.qb.from_(ple)
		.select(ple.account_currency, Abs(Sum(ple.amount_in_account_currency)).as_("amount"))
		.where((ple.party == party) & (ple.docstatus == 1) & (ple.company == doc.company))
	)

	if doc.doctype == "Sales Order":
		si = frappe.qb.DocType("Sales Invoice")
		sii = frappe.qb.DocType("Sales Invoice Item")
		down_payment_invoices = (
			frappe.qb.from_(si)
			.select(si.name)
			.left_join(sii)
			.on(sii.parent == si.name)
			.where((si.is_down_payment_invoice == 1) & (sii.sales_order == doc.name))
			.run(as_list=True)
		)

		if down_payment_invoices and down_payment_invoices[0]:
			advance_query = advance_query.where(
				(
					(ple.against_voucher_type == doc.doctype)
					& (ple.against_voucher_no == doc.name))
				& (ple.voucher_type == "Payment Entry")
				| (
					(ple.against_voucher_type == "Sales Invoice")
					& (ple.against_voucher_no.isin(down_payment_invoices[0]))
					& (ple.voucher_type == "Payment Entry")
				)
			)
		else:
			advance_query = advance_query.where(
				(ple.against_voucher_type == doc.doctype) & (ple.against_voucher_no == doc.name)
			)

	else:
		advance_query = advance_query.where(
			(ple.against_voucher_type == doc.doctype) & (ple.against_voucher_no == doc.name)
		)

	advance = advance_query.run(as_dict=True)

	if advance:
		advance = advance[0]

		advance_paid = flt(advance.amount, doc.precision("advance_paid"))
		formatted_advance_paid = fmt_money(
			advance_paid, precision=doc.precision("advance_paid"), currency=advance.account_currency
		)

		frappe.db.set_value(doc.doctype, doc.name, "party_account_currency", advance.account_currency)

		if advance.account_currency == doc.currency:
			order_total = doc.get("rounded_total") or doc.grand_total
			precision = "rounded_total" if doc.get("rounded_total") else "grand_total"
		else:
			order_total = doc.get("base_rounded_total") or doc.base_grand_total
			precision = "base_rounded_total" if doc.get("base_rounded_total") else "base_grand_total"

		formatted_order_total = fmt_money(
			order_total, precision=doc.precision(precision), currency=advance.account_currency
		)

		if doc.currency == doc.company_currency and advance_paid > order_total:
			frappe.throw(
				_(
					"Total advance ({0}) against Order {1} cannot be greater than the Grand Total ({2})"
				).format(formatted_advance_paid, doc.name, formatted_order_total)
			)

		frappe.db.set_value(doc.doctype, doc.name, "advance_paid", advance_paid)


def make_exchange_gain_loss_gl_entries(doc, gl_entries):
	if doc.get("doctype") not in ["Purchase Invoice", "Sales Invoice"]:
		return

	for d in doc.get("advances"):
		if not d.exchange_gain_loss:
			continue

		is_purchase_invoice = doc.get("doctype") == "Purchase Invoice"
		party = doc.supplier if is_purchase_invoice else doc.customer
		party_account = doc.credit_to if is_purchase_invoice else doc.debit_to
		party_type = "Supplier" if is_purchase_invoice else "Customer"

		gain_loss_account = frappe.db.get_value("Company", doc.company, "exchange_gain_loss_account")
		if not gain_loss_account:
			frappe.throw(
				_("Please set default Exchange Gain/Loss Account in Company {}").format(doc.get("company"))
			)
		account_currency = get_account_currency(gain_loss_account)
		if account_currency != doc.company_currency:
			frappe.throw(
				_("Currency for {0} must be {1}").format(gain_loss_account, doc.company_currency)
			)

		# for purchase
		dr_or_cr = "debit" if d.exchange_gain_loss > 0 else "credit"
		if not is_purchase_invoice:
			# just reverse for sales?
			dr_or_cr = "debit" if dr_or_cr == "credit" else "credit"

		gl_entries.append(
			doc.get_gl_dict(
				{
					"account": gain_loss_account,
					"account_currency": account_currency,
					"against": party,
					dr_or_cr + "_in_account_currency": abs(d.exchange_gain_loss),
					dr_or_cr: abs(d.exchange_gain_loss),
					"cost_center": doc.cost_center or erpnext.get_default_cost_center(doc.company),
					"project": doc.project,
					"accounting_journal": doc.accounting_journal,
				},
				item=d,
			)
		)

		dr_or_cr = "debit" if dr_or_cr == "credit" else "credit"

		gl_entries.append(
			doc.get_gl_dict(
				{
					"account": party_account,
					"party_type": party_type,
					"party": party,
					"against": gain_loss_account,
					dr_or_cr + "_in_account_currency": flt(abs(d.exchange_gain_loss) / doc.conversion_rate),
					dr_or_cr: abs(d.exchange_gain_loss),
					"cost_center": doc.cost_center,
					"project": doc.project,
					"accounting_journal": doc.accounting_journal,
				},
				doc.party_account_currency,
				item=doc,
			)
		)


def get_advance_payment_entries(
		party_type,
		party,
		party_account,
		order_doctype,
		order_list=None,
):
	party_account_field = "paid_from" if party_type == "Customer" else "paid_to"
	currency_field = (
		"paid_from_account_currency" if party_type == "Customer" else "paid_to_account_currency"
	)
	payment_type = "Receive" if party_type == "Customer" else "Pay"
	exchange_rate_field = (
		"source_exchange_rate" if payment_type == "Receive" else "target_exchange_rate"
	)

	payment_entries_against_order, unallocated_payment_entries = [], []
	pe = frappe.qb.DocType("Payment Entry")
	per = frappe.qb.DocType("Payment Entry Reference")

	if order_list:
		payment_entries_against_order = (
			frappe.qb.from_(pe)
			.left_join(per)
			.on(pe.name == per.parent)
			.select(
				ConstantColumn("Payment Entry").as_("reference_type"),
				pe.name.as_('reference_name'),
				pe.remarks,
				per.allocated_amount.as_('amount'),
				per.name.as_('reference_row'),
				per.reference_doctype.as_('against_order_type'),
				per.reference_name.as_('against_order'),
				pe.posting_date,
				pe[currency_field].as_('currency'),
				pe[exchange_rate_field].as_('exchange_rate'),
			)
			.where(pe[party_account_field].isin(party_account))
			.where(pe.payment_type == payment_type)
			.where(pe.party_type == party_type)
			.where(pe.party == party)
			.where(pe.docstatus == 1)
			.where(per.reference_doctype == order_doctype)
			.where(per.reference_name.isin(order_list))
			.orderby(pe.posting_date)
			.run(as_dict=True)
		)

	return list(payment_entries_against_order)
