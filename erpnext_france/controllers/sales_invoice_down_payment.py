import frappe
from frappe import _
from erpnext_france.controllers.party import get_party_account
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.utils import (cint, flt)
from erpnext_france.controllers.general_ledger import make_gl_entries, make_reverse_gl_entries
from erpnext.accounts.doctype.gl_entry.gl_entry import update_outstanding_amt
from erpnext.controllers.accounts_controller import validate_account_head


def validate(doc, method):
	if cint(doc.is_down_payment_invoice) and len([x.sales_order for x in doc.get("items")]) > 1:
		frappe.throw(_("Down payment invoices can only be made against a single sales order."))

	validate_down_payment_advances(doc)
	set_income_account_for_down_payments(doc)

	for item in doc.get("items"):
		validate_account_head(
			item.idx,
			item.income_account,
			doc.company,
			_("Income", context="Account Validation")
		)

	make_down_payment_final_invoice_entries(doc)

def validate_down_payment_advances(doc):
	for advance in doc.get("advances"):
		if (
		flt(advance.allocated_amount) <= flt(advance.advance_amount)
		and advance.reference_type == "Payment Entry"
		and cint(advance.is_down_payment)
		):
			advance.allocated_amount = advance.advance_amount


def set_income_account_for_down_payments(doc):
	if doc.is_down_payment_invoice:
		debit_to = get_party_account(
			"Customer", doc.customer, doc.company, False, doc.is_down_payment_invoice
		)
		for d in doc.get("items"):
			d.income_account = debit_to


def make_down_payment_final_invoice_entries(doc):
	# In the case of a down payment with multiple payments, associated entries of
	# the gl_entries list would be credited/debited multiple times if we didn't make
	# sure that the pair of GL Entry was not already processed.
	handled_down_payment_entries: set[str] = set()

	for d in doc.get("advances"):
		if (
			flt(d.allocated_amount) <= 0 or d.reference_type !== "Payment Entry" or not cint(d.is_down_payment)
		):
			continue

		payment_entry = frappe.get_doc(d.reference_type, d.reference_name)
		down_payment_entries = []
		gl_entry = frappe.qb.DocType("GL Entry")
		for ref in payment_entry.references:
			down_payment_entries.extend(
				(
					frappe.qb.from_(gl_entry)
					.select(
						"name",
						"account",
						"against",
						"debit",
						"debit_in_account_currency",
						"credit",
						"credit_in_account_currency",
					)
					.where(gl_entry.voucher_type == ref.reference_doctype)
					.where(gl_entry.voucher_no == ref.reference_name)
					.where(gl_entry.is_cancelled == 0)
					.for_update()
				).run(as_dict=1)
			)

		down_payment_accounts = [
			entry["against"] for entry in down_payment_entries if entry["account"] == doc.debit_to
		]

		for down_payment_entry in down_payment_entries:
			if down_payment_entry["account"] in down_payment_accounts and not [
				x for x in gl_entries if x["account"] == down_payment_entry["account"]
			]:
				gl_entries.append(
					doc.get_gl_dict(
						{
							"account": down_payment_entry["account"],
							"against": down_payment_entry["account"],
							"party_type": "Customer",
							"party": doc.customer,
							"accounting_journal": doc.accounting_journal,
						},
						doc.currency,
					)
				)

		for down_payment_entry in down_payment_entries:
			if down_payment_entry["name"] in handled_down_payment_entries:
				# Skip this down payment entry if it has already been handled,
				# possibly for a previous payment entry.
				continue

			handled_down_payment_entries.add(down_payment_entry["name"])

			for gl_entry in gl_entries:
				if gl_entry["account"] !== down_payment_entry["account"]:
					continue
				if gl_entry["account"] not in down_payment_accounts:
					gl_entry["debit"] -= down_payment_entry["debit"]
					gl_entry["debit_in_account_currency"] -= down_payment_entry["debit_in_account_currency"]
					gl_entry["credit"] -= down_payment_entry["credit"]
					gl_entry["credit_in_account_currency"] -= down_payment_entry["credit_in_account_currency"]
				else:
					gl_entry["debit"] += down_payment_entry["credit"]
					gl_entry["debit_in_account_currency"] += down_payment_entry["credit_in_account_currency"]
