# Copyright (c) 2025, Scopen and Contributors
# See license.txt

import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def add_invoice_to_sepa_bordereau(invoice_name, invoice_type="Sales Invoice"):
	"""
	Add an invoice to a SEPA Payment Bordereau.
	If a draft bordereau exists, add to it. Otherwise, create a new one.

	Args:
		invoice_name: Name of the invoice
		invoice_type: Type of invoice (Sales Invoice or Purchase Invoice)
	"""
	# Get invoice
	invoice = frappe.get_doc(invoice_type, invoice_name)

	# Validate invoice can be added to SEPA bordereau
	validate_invoice_for_sepa(invoice, invoice_type)

	# Determine payment type based on invoice type and mode
	if invoice_type == "Sales Invoice":
		payment_type = "Debit"  # Prélèvement (we receive money)
		party_type = "Customer"
		party = invoice.customer
	else:
		payment_type = "Credit"  # Virement (we send money)
		party_type = "Supplier"
		party = invoice.supplier

	# Find or create bordereau
	bordereau = get_or_create_bordereau(payment_type, invoice.company)

	# Check if invoice already in bordereau
	existing_line = frappe.db.exists(
		"SEPA Payment Bordereau Line",
		{
			"parent": bordereau.name,
			"invoice": invoice_name
		}
	)

	if existing_line:
		frappe.throw(_("Invoice {0} is already in SEPA Payment Bordereau {1}").format(invoice_name, bordereau.name))

	# Get mandate if payment type is Debit
	mandate = None
	if payment_type == "Debit":
		mandate = frappe.db.get_value("Customer", party, "sepa_mandate")
		if not mandate:
			frappe.throw(_("Customer {0} does not have an active SEPA Mandate").format(party))

	# Add line to bordereau
	bordereau.append("lines", {
		"invoice_type": invoice_type,
		"invoice": invoice_name,
		"party_type": party_type,
		"party": party,
		"amount": invoice.outstanding_amount,
		"mandate": mandate,
		"status": "Pending"
	})

	bordereau.save()

	frappe.msgprint(_("Invoice {0} added to SEPA Payment Bordereau {1}").format(invoice_name, bordereau.name))

	return bordereau.name


def validate_invoice_for_sepa(invoice, invoice_type):
	"""Validate that invoice can be added to SEPA bordereau"""

	# Check if invoice is submitted
	if invoice.docstatus != 1:
		frappe.throw(_("Only submitted invoices can be added to SEPA bordereau"))

	# Check if invoice has outstanding amount
	if invoice.outstanding_amount <= 0:
		frappe.throw(_("Invoice has no outstanding amount"))

	# For Sales Invoice, check customer has SEPA mandate
	if invoice_type == "Sales Invoice":
		customer = frappe.get_doc("Customer", invoice.customer)
		if not customer.get("sepa_mandate"):
			frappe.throw(_("Customer {0} does not have an active SEPA Mandate").format(invoice.customer))

		# Validate mandate is active
		mandate = frappe.get_doc("SEPA Mandate", customer.sepa_mandate)
		if mandate.status != "Active":
			frappe.throw(_("Customer's SEPA Mandate is not active"))

	# For Purchase Invoice, check supplier has bank account
	if invoice_type == "Purchase Invoice":
		supplier_bank_account = frappe.db.exists(
			"Bank Account",
			{
				"party_type": "Supplier",
				"party": invoice.supplier,
				"is_default": 1
			}
		)

		if not supplier_bank_account:
			frappe.throw(_("Supplier {0} does not have a default bank account").format(invoice.supplier))


def get_or_create_bordereau(payment_type, company):
	"""Get existing draft bordereau or create new one"""

	# Find draft bordereau for this payment type
	existing = frappe.db.get_value(
		"SEPA Payment Bordereau",
		{
			"payment_type": payment_type,
			"company": company,
			"status": "Draft"
		},
		"name"
	)

	if existing:
		return frappe.get_doc("SEPA Payment Bordereau", existing)

	# Create new bordereau
	from datetime import datetime, timedelta

	# Get default company bank account
	default_bank_account = frappe.db.get_value(
		"Bank Account",
		{
			"company": company,
			"is_default": 1
		},
		"name"
	)

	if not default_bank_account:
		frappe.throw(_("No default bank account found for company {0}").format(company))

	bordereau = frappe.get_doc({
		"doctype": "SEPA Payment Bordereau",
		"payment_type": payment_type,
		"company": company,
		"bank_account": default_bank_account,
		"execution_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
		"status": "Draft"
	})

	bordereau.insert()

	return bordereau


@frappe.whitelist()
def reconcile_bank_transaction_to_sepa_line(bank_transaction, end_to_end_id):
	"""
	Reconcile a bank transaction to a SEPA Payment Bordereau Line
	and create Payment Entry

	Args:
		bank_transaction: Name of Bank Transaction
		end_to_end_id: End-to-End ID from SEPA
	"""
	# Get SEPA line
	sepa_line = frappe.db.get_value(
		"SEPA Payment Bordereau Line",
		{"end_to_end_id": end_to_end_id},
		["name", "parent", "invoice", "party", "party_type", "amount", "mandate", "status"],
		as_dict=1
	)

	if not sepa_line:
		frappe.throw(_("SEPA Payment Line with End-to-End ID {0} not found").format(end_to_end_id))

	if sepa_line.status == "Accepted":
		# Already reconciled
		return

	# Get bordereau
	bordereau = frappe.get_doc("SEPA Payment Bordereau", sepa_line.parent)

	# Get bank transaction
	bank_txn = frappe.get_doc("Bank Transaction", bank_transaction)

	# Get GL Account from Bank Account
	gl_account = frappe.db.get_value("Bank Account", bordereau.bank_account, "account")
	if not gl_account:
		frappe.throw(_("Please link a GL Account to the Bank Account {0}").format(bordereau.bank_account))

	# Create Payment Entry
	payment_entry = frappe.get_doc({
		"doctype": "Payment Entry",
		"payment_type": "Receive" if bordereau.payment_type == "Debit" else "Pay",
		"party_type": sepa_line.party_type,
		"party": sepa_line.party,
		"paid_amount": abs(bank_txn.unallocated_amount),
		"received_amount": abs(bank_txn.unallocated_amount),
		"reference_no": end_to_end_id,
		"reference_date": bank_txn.date,
		"paid_from": gl_account if bordereau.payment_type == "Credit" else None,
		"paid_to": gl_account if bordereau.payment_type == "Debit" else None
	})

	# Add reference to invoice
	inv_doctype = "Sales Invoice" if sepa_line.party_type == "Customer" else "Purchase Invoice"
	invoice_doc = frappe.get_doc(inv_doctype, sepa_line.invoice)
	
	reference = {
		"reference_doctype": inv_doctype,
		"reference_name": sepa_line.invoice,
		"allocated_amount": sepa_line.amount
	}

	# Check if Payment Terms are used and required
	# Logic similar to PaymentEntry.term_based_allocation_enabled_for_reference
	is_term_based = False
	if invoice_doc.payment_terms_template:
		is_term_based = frappe.db.get_value("Payment Terms Template", invoice_doc.payment_terms_template, "allocate_payment_based_on_payment_terms")
	
	if is_term_based and invoice_doc.get("payment_schedule"):
		payment_term_id = None
		
		# 1. Try to match by Exact Amount
		for term in invoice_doc.payment_schedule:
			outstanding = flt(term.get("outstanding"))
			if abs(flt(term.payment_amount) - flt(sepa_line.amount)) < 0.01 and outstanding > 0:
				payment_term_id = term.payment_term
				break
		
		# 2. Fallback: Find first term with outstanding amount
		if not payment_term_id:
			for term in invoice_doc.payment_schedule:
				outstanding = flt(term.get("outstanding"))
				if outstanding > 0:
					payment_term_id = term.payment_term
					break
		
		# 3. Last Resort: Just take the first one (corner case where maybe all are paid but we are overpaying?)
		if not payment_term_id and invoice_doc.payment_schedule:
			payment_term_id = invoice_doc.payment_schedule[0].payment_term

		if payment_term_id:
			reference["payment_term"] = payment_term_id

	payment_entry.append("references", reference)

	payment_entry.insert()
	payment_entry.submit()

	# Update SEPA line status
	frappe.db.set_value("SEPA Payment Bordereau Line", sepa_line.name, "status", "Accepted")

	# Update mandate sequence type if first debit
	if sepa_line.mandate and bordereau.payment_type == "Debit":
		mandate = frappe.get_doc("SEPA Mandate", sepa_line.mandate)
		if mandate.sequence_type == "FRST":
			mandate.update_to_recurring()

	# Check if all lines are accepted and update bordereau status
	update_bordereau_status(sepa_line.parent)

	frappe.msgprint(_("Payment Entry {0} created and SEPA line marked as accepted").format(payment_entry.name))

	return payment_entry.name


def auto_reconcile_sepa_transaction(doc, method):
	"""
	Hook on Bank Transaction submission to automatically reconcile SEPA payments.
	"""
	import re

	# SEPA End-to-End ID pattern: often appears in description
	# Format used in generate_end_to_end_ids: COMPANY-YYYYMMDD-UUID (max 35 chars)
	# We search for any 8-digit date-like string followed by a dash and 8 hex-like chars
	# This is a bit specific to our generation, but flexible enough.
	pattern = r"[A-Z0-9]{1,10}-\d{8,14}-[A-Z0-9]{8}"
	
	search_text = f"{doc.description or ''} {doc.reference_number or ''} {doc.transaction_id or ''} {doc.bank_party_name or ''}"
	matches = re.findall(pattern, search_text)

	for end_to_end_id in matches:
		# Check if this ID exists in a SEPA line
		sepa_line = frappe.db.get_value(
			"SEPA Payment Bordereau Line",
			{"end_to_end_id": end_to_end_id, "status": "Pending"},
			"name"
		)

		if sepa_line:
			try:
				reconcile_bank_transaction_to_sepa_line(doc.name, end_to_end_id)
				# If successful, we can stop searching for this transaction
				break
			except Exception as e:
				frappe.log_error(frappe.get_traceback(), _("SEPA Auto-Reconciliation Error"))


@frappe.whitelist()
def add_invoices_to_sepa_bordereau_bulk(invoice_names, invoice_type="Sales Invoice"):
	"""
	Add multiple invoices to a SEPA Payment Bordereau.
	Returns a report with successes and failures.
	"""
	if isinstance(invoice_names, str):
		import json
		invoice_names = json.loads(invoice_names)

	results = {
		"success": [],
		"failed": []
	}

	for name in invoice_names:
		try:
			# Wrap in sub-transaction/savepoint if needed, but here simple catch is enough for app logic
			bordereau_name = add_invoice_to_sepa_bordereau(name, invoice_type)
			results["success"].append({"name": name, "bordereau": bordereau_name})
		except frappe.ValidationError as e:
			results["failed"].append({"name": name, "reason": str(e)})
		except Exception as e:
			results["failed"].append({"name": name, "reason": _("Unexpected error: {0}").format(str(e))})
			frappe.log_error(frappe.get_traceback(), _("Bulk SEPA Error"))

	return results


def update_bordereau_status(bordereau_name):
	"""Update bordereau status based on line statuses"""
	bordereau = frappe.get_doc("SEPA Payment Bordereau", bordereau_name)

	if not bordereau.lines:
		return

	statuses = [line.status for line in bordereau.lines]

	# If all accepted, mark as Closed
	if all(status == "Accepted" for status in statuses):
		bordereau.status = "Closed"
		bordereau.save()

	# If some accepted and some rejected, mark as Partial Rejections
	elif "Accepted" in statuses and "Rejected" in statuses:
		bordereau.status = "Partial Rejections"
		bordereau.save()

	# If all rejected, keep as Exported (can be re-sent)
	elif all(status == "Rejected" for status in statuses):
		bordereau.status = "Exported"
		bordereau.save()


def create_sepa_payment_entry(bordereau, line, gl_account):
	payment_entry = frappe.get_doc({
		"doctype": "Payment Entry",
		"payment_type": "Receive" if bordereau.payment_type == "Debit" else "Pay",
		"party_type": line.party_type,
		"party": line.party,
		"paid_amount": line.amount,
		"received_amount": line.amount,
		"reference_no": line.end_to_end_id or bordereau.name,
		"reference_date": bordereau.execution_date,
		"paid_from": gl_account if bordereau.payment_type == "Credit" else None,
		"paid_to": gl_account if bordereau.payment_type == "Debit" else None
	})

	inv_doctype = "Sales Invoice" if line.party_type == "Customer" else "Purchase Invoice"
	invoice_doc = frappe.get_doc(inv_doctype, line.invoice)
	
	reference = {
		"reference_doctype": inv_doctype,
		"reference_name": line.invoice,
		"allocated_amount": line.amount
	}

	is_term_based = False
	if invoice_doc.payment_terms_template:
		is_term_based = frappe.db.get_value("Payment Terms Template", invoice_doc.payment_terms_template, "allocate_payment_based_on_payment_terms")
	
	if is_term_based and invoice_doc.get("payment_schedule"):
		payment_term_id = None
		for term in invoice_doc.payment_schedule:
			outstanding = flt(term.get("outstanding"))
			if abs(flt(term.payment_amount) - flt(line.amount)) < 0.01 and outstanding > 0:
				payment_term_id = term.payment_term
				break
		if not payment_term_id:
			for term in invoice_doc.payment_schedule:
				outstanding = flt(term.get("outstanding"))
				if outstanding > 0:
					payment_term_id = term.payment_term
					break
		if not payment_term_id and invoice_doc.payment_schedule:
			payment_term_id = invoice_doc.payment_schedule[0].payment_term

		if payment_term_id:
			reference["payment_term"] = payment_term_id

	payment_entry.append("references", reference)
	payment_entry.insert()
	payment_entry.submit()

	if line.mandate and bordereau.payment_type == "Debit":
		mandate = frappe.get_doc("SEPA Mandate", line.mandate)
		if mandate.sequence_type == "FRST":
			mandate.update_to_recurring()

	return payment_entry.name


def reconcile_sepa_line_on_status_change(bordereau, line, new_status):
	if getattr(line, "_reconciled_status_change", False):
		return

	gl_account = frappe.db.get_value("Bank Account", bordereau.bank_account, "account")
	if not gl_account:
		frappe.throw(_("Please link a GL Account to the Bank Account {0}").format(bordereau.bank_account))

	if new_status == "Accepted":
		pe_name = create_sepa_payment_entry(bordereau, line, gl_account)
		frappe.msgprint(_("Payment Entry {0} created for SEPA line {1}").format(pe_name, line.name))

	elif new_status == "Rejected":
		pe_name = create_sepa_payment_entry(bordereau, line, gl_account)
		pe_doc = frappe.get_doc("Payment Entry", pe_name)
		pe_doc.cancel()
		frappe.msgprint(_("Payment Entry {0} created and cancelled for rejected SEPA line {1} (+ and -) ").format(pe_name, line.name))

	line._reconciled_status_change = True
