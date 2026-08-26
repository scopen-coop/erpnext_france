# Copyright (c) 2025, Scopen and Contributors
# See license.txt

import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def add_invoice_to_sepa_bordereau(invoice_name: str, invoice_type: str = "Sales Invoice"):
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

	available = get_invoice_sepa_available_amount(
		invoice_name,
		invoice_type,
		current_bordereau=bordereau.name,
	)
	if flt(available) <= 0:
		frappe.throw(
			_("Invoice {0} has no remaining amount available for SEPA bordereaux").format(invoice_name)
		)

	# Get mandate if payment type is Debit
	mandate = None
	if payment_type == "Debit":
		mandate = frappe.db.get_value("Customer", party, "sepa_mandate")
		if not mandate:
			frappe.throw(_("Customer {0} does not have an active SEPA Mandate").format(party))

	# Add line to bordereau
	bordereau.append(
		"lines",
		{
			"invoice_type": invoice_type,
			"invoice": invoice_name,
			"party_type": party_type,
			"party": party,
			"amount": available,
			"mandate": mandate,
			"status": "Pending",
		},
	)

	bordereau.save()
	sync_invoice_sepa_bordereau_link(invoice_name, invoice_type)

	frappe.msgprint(_("Invoice {0} added to SEPA Payment Bordereau {1}").format(invoice_name, bordereau.name))

	return bordereau.name


def get_invoice_sepa_bordereau_info(invoice_name, invoice_type="Sales Invoice"):
	"""Return the most relevant SEPA bordereau for an invoice, if any."""
	lines = frappe.get_all(
		"SEPA Payment Bordereau Line",
		filters={"invoice": invoice_name, "invoice_type": invoice_type},
		fields=["parent", "status", "modified"],
		order_by="modified desc",
	)
	if not lines:
		return None

	for line in lines:
		bordereau_status = frappe.db.get_value("SEPA Payment Bordereau", line.parent, "status")
		if bordereau_status != "Closed":
			return {"bordereau": line.parent, "line_status": line.status}

	return {"bordereau": lines[0].parent, "line_status": lines[0].status}


def sync_invoice_sepa_bordereau_link(invoice_name, invoice_type="Sales Invoice"):
	"""Update Sales Invoice fields that show SEPA bordereau membership."""
	if invoice_type != "Sales Invoice":
		return

	if not frappe.db.has_column("Sales Invoice", "sepa_payment_bordereau"):
		return

	info = get_invoice_sepa_bordereau_info(invoice_name, invoice_type)
	frappe.db.set_value(
		"Sales Invoice",
		invoice_name,
		{
			"sepa_payment_bordereau": info["bordereau"] if info else None,
			"sepa_bordereau_line_status": info["line_status"] if info else None,
		},
		update_modified=False,
	)


def sync_invoices_sepa_bordereau_links(invoices):
	"""Update SEPA bordereau link fields for multiple invoices."""
	seen = set()
	for invoice_name, invoice_type in invoices:
		key = (invoice_name, invoice_type)
		if key in seen:
			continue
		seen.add(key)
		sync_invoice_sepa_bordereau_link(invoice_name, invoice_type)


def get_invoice_pending_sepa_lines(
	invoice_name,
	invoice_type,
	current_line_name=None,
):
	"""Return Pending SEPA lines that reserve amount for an invoice (non-Closed bordereaux)."""
	if not invoice_name:
		return []

	lines = frappe.get_all(
		"SEPA Payment Bordereau Line",
		filters={"invoice": invoice_name, "invoice_type": invoice_type, "status": "Pending"},
		fields=["name", "parent", "amount", "status"],
	)

	pending = []
	for line in lines:
		if current_line_name and line.name == current_line_name:
			continue

		bordereau_status = frappe.db.get_value("SEPA Payment Bordereau", line.parent, "status")
		if bordereau_status == "Closed":
			continue

		pending.append(line)

	return pending


def get_invoice_amount_reserved_in_sepa(
	invoice_name,
	invoice_type,
	current_bordereau=None,
	current_line_name=None,
):
	"""Sum of Pending amounts reserved for an invoice on non-Closed SEPA bordereaux."""
	lines = get_invoice_pending_sepa_lines(
		invoice_name,
		invoice_type,
		current_line_name=current_line_name,
	)
	return sum(flt(line.amount) for line in lines)


def get_invoice_sepa_available_amount(
	invoice_name,
	invoice_type="Sales Invoice",
	current_bordereau=None,
	current_line_name=None,
	outstanding_amount=None,
):
	"""Outstanding left after Pending SEPA reservations (excluding current line)."""
	if not invoice_name:
		return 0

	if outstanding_amount is None:
		outstanding_amount = frappe.db.get_value(invoice_type, invoice_name, "outstanding_amount") or 0

	reserved = get_invoice_amount_reserved_in_sepa(
		invoice_name,
		invoice_type,
		current_bordereau=current_bordereau,
		current_line_name=current_line_name,
	)
	return max(flt(outstanding_amount) - flt(reserved), 0)


@frappe.whitelist()
def get_invoice_sepa_available_amount_for_ui(
	invoice_name: str,
	invoice_type: str = "Sales Invoice",
	current_bordereau: str | None = None,
	current_line_name: str | None = None,
):
	"""Whitelist wrapper for bordereau form default amount."""
	return get_invoice_sepa_available_amount(
		invoice_name,
		invoice_type,
		current_bordereau=current_bordereau or None,
		current_line_name=current_line_name or None,
	)


def validate_invoice_amount_in_bordereaux(
	invoice_name,
	invoice_type,
	amount,
	current_bordereau=None,
	current_line_name=None,
	row_idx=None,
):
	"""Ensure line amount does not exceed remaining SEPA-available outstanding."""
	if not invoice_name:
		return

	amount = flt(amount)
	if amount <= 0:
		return

	outstanding = flt(frappe.db.get_value(invoice_type, invoice_name, "outstanding_amount") or 0)
	pending_lines = get_invoice_pending_sepa_lines(
		invoice_name,
		invoice_type,
		current_line_name=current_line_name,
	)
	reserved = sum(flt(line.amount) for line in pending_lines)
	available = outstanding - reserved

	if amount <= available + 0.00001:
		return

	reserving = sorted({line.parent for line in pending_lines})
	amount_fmt = frappe.format_value(amount, {"fieldtype": "Currency"})
	available_fmt = frappe.format_value(max(available, 0), {"fieldtype": "Currency"})
	outstanding_fmt = frappe.format_value(outstanding, {"fieldtype": "Currency"})
	reserved_fmt = frappe.format_value(reserved, {"fieldtype": "Currency"})

	if reserving:
		if row_idx:
			frappe.throw(
				_(
					"Row {0}: Amount {1} for invoice {2} exceeds remaining available {3}"
					" (outstanding {4} minus {5} reserved on {6})"
				).format(
					row_idx,
					amount_fmt,
					invoice_name,
					available_fmt,
					outstanding_fmt,
					reserved_fmt,
					", ".join(reserving),
				)
			)
		frappe.throw(
			_(
				"Amount {0} for invoice {1} exceeds remaining available {2}"
				" (outstanding {3} minus {4} reserved on {5})"
			).format(
				amount_fmt,
				invoice_name,
				available_fmt,
				outstanding_fmt,
				reserved_fmt,
				", ".join(reserving),
			)
		)

	if row_idx:
		frappe.throw(
			_("Row {0}: Amount {1} for invoice {2} exceeds outstanding {3}").format(
				row_idx,
				amount_fmt,
				invoice_name,
				outstanding_fmt,
			)
		)
	frappe.throw(
		_("Amount {0} for invoice {1} exceeds outstanding {2}").format(
			amount_fmt,
			invoice_name,
			outstanding_fmt,
		)
	)


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
			"Bank Account", {"party_type": "Supplier", "party": invoice.supplier, "is_default": 1}
		)

		if not supplier_bank_account:
			frappe.throw(_("Supplier {0} does not have a default bank account").format(invoice.supplier))


def is_company_bank_account(bank_account, company):
	"""Return whether the Bank Account belongs to the company itself."""
	if not bank_account or not company:
		return False

	bank = frappe.db.get_value(
		"Bank Account",
		bank_account,
		["company", "is_company_account", "party_type", "party", "disabled"],
		as_dict=True,
	)
	if not bank or bank.disabled:
		return False

	return bool(
		bank.company == company and bank.is_company_account and not bank.party_type and not bank.party
	)


def get_default_company_bank_account(company):
	"""Get the default company-owned Bank Account for a company."""
	company_default_account = frappe.get_cached_value("Company", company, "default_bank_account")

	if company_default_account:
		for row in frappe.get_all(
			"Bank Account",
			filters={
				"company": company,
				"account": company_default_account,
				"is_company_account": 1,
				"disabled": 0,
			},
			fields=["name", "party_type", "party"],
			order_by="is_default desc, modified desc",
		):
			if not row.party_type and not row.party:
				return row.name

	for row in frappe.get_all(
		"Bank Account",
		filters={
			"company": company,
			"is_company_account": 1,
			"is_default": 1,
			"disabled": 0,
		},
		fields=["name", "party_type", "party"],
		order_by="modified desc",
	):
		if not row.party_type and not row.party:
			return row.name

	frappe.throw(_("No default company bank account found for company {0}").format(company))


def ensure_bordereau_bank_account(bordereau, company=None):
	"""Ensure a draft bordereau uses a real company bank account."""
	company = company or bordereau.company
	if not company:
		return False

	if is_company_bank_account(bordereau.bank_account, company):
		return False

	bordereau.bank_account = get_default_company_bank_account(company)
	return True


def get_or_create_bordereau(payment_type, company):
	"""Get existing draft bordereau or create new one"""

	# Find draft bordereau for this payment type
	existing = frappe.db.get_value(
		"SEPA Payment Bordereau",
		{"payment_type": payment_type, "company": company, "status": "Draft"},
		"name",
	)

	if existing:
		bordereau = frappe.get_doc("SEPA Payment Bordereau", existing)
		if ensure_bordereau_bank_account(bordereau, company):
			bordereau.save()
		return bordereau

	# Create new bordereau
	from datetime import datetime, timedelta

	default_bank_account = get_default_company_bank_account(company)

	bordereau = frappe.get_doc(
		{
			"doctype": "SEPA Payment Bordereau",
			"payment_type": payment_type,
			"company": company,
			"bank_account": default_bank_account,
			"execution_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
			"status": "Draft",
		}
	)

	bordereau.insert()

	return bordereau


@frappe.whitelist()
def reconcile_bank_transaction_to_sepa_line(bank_transaction: str, end_to_end_id: str):
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
		as_dict=1,
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
	remittance_info = get_sepa_line_remittance_info(sepa_line)
	invoice_reference = get_sepa_line_invoice_reference(sepa_line)
	payment_type, account_fields = get_sepa_payment_entry_account_fields(bordereau, sepa_line, gl_account)

	pe_data = {
		"doctype": "Payment Entry",
		"payment_type": payment_type,
		"company": bordereau.company,
		"party_type": sepa_line.party_type,
		"party": sepa_line.party,
		"paid_amount": abs(bank_txn.unallocated_amount),
		"received_amount": abs(bank_txn.unallocated_amount),
		"posting_date": bank_txn.date or bordereau.execution_date,
		"reference_no": invoice_reference,
		"reference_date": bank_txn.date or bordereau.execution_date,
		"remarks": remittance_info,
		"bank_account": bordereau.bank_account,
		**account_fields,
	}
	if frappe.db.has_column("Payment Entry", "sepa_payment_bordereau"):
		pe_data["sepa_payment_bordereau"] = bordereau.name

	payment_entry = frappe.get_doc(pe_data)

	# Add reference to invoice
	inv_doctype = "Sales Invoice" if sepa_line.party_type == "Customer" else "Purchase Invoice"
	invoice_doc = frappe.get_doc(inv_doctype, sepa_line.invoice)

	reference = {
		"reference_doctype": inv_doctype,
		"reference_name": sepa_line.invoice,
		"allocated_amount": sepa_line.amount,
	}

	# Check if Payment Terms are used and required
	# Logic similar to PaymentEntry.term_based_allocation_enabled_for_reference
	is_term_based = False
	if invoice_doc.payment_terms_template:
		is_term_based = frappe.db.get_value(
			"Payment Terms Template",
			invoice_doc.payment_terms_template,
			"allocate_payment_based_on_payment_terms",
		)

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
	line_updates = {"status": "Accepted"}
	if frappe.db.has_column("SEPA Payment Bordereau Line", "payment_entry"):
		line_updates["payment_entry"] = payment_entry.name
	frappe.db.set_value("SEPA Payment Bordereau Line", sepa_line.name, line_updates)
	sync_invoice_sepa_bordereau_link(
		sepa_line.invoice,
		sepa_line.get("invoice_type")
		or ("Sales Invoice" if sepa_line.party_type == "Customer" else "Purchase Invoice"),
	)

	# Update mandate sequence type if first debit
	if sepa_line.mandate and bordereau.payment_type == "Debit":
		mandate = frappe.get_doc("SEPA Mandate", sepa_line.mandate)
		if mandate.sequence_type == "FRST":
			mandate.update_to_recurring()

	# Check if all lines are accepted and update bordereau status
	update_bordereau_status(sepa_line.parent)

	frappe.msgprint(
		_("Payment Entry {0} created and SEPA line marked as accepted").format(payment_entry.name)
	)

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
			"SEPA Payment Bordereau Line", {"end_to_end_id": end_to_end_id, "status": "Pending"}, "name"
		)

		if sepa_line:
			try:
				reconcile_bank_transaction_to_sepa_line(doc.name, end_to_end_id)
				# If successful, we can stop searching for this transaction
				break
			except Exception:
				frappe.log_error(frappe.get_traceback(), _("SEPA Auto-Reconciliation Error"))


@frappe.whitelist()
def add_invoices_to_sepa_bordereau_bulk(invoice_names: list | str, invoice_type: str = "Sales Invoice"):
	"""
	Add multiple invoices to a SEPA Payment Bordereau.
	Returns a report with successes and failures.
	"""
	if isinstance(invoice_names, str):
		import json

		invoice_names = json.loads(invoice_names)

	results = {"success": [], "failed": []}

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


def get_sepa_line_invoice_reference(line):
	"""Return the document reference shown to customers/suppliers on bank statements."""
	document_ref = _sepa_line_value(line, "document_ref")
	invoice = _sepa_line_value(line, "invoice")
	if document_ref and not invoice:
		return document_ref

	invoice_type = _sepa_line_value(line, "invoice_type") or (
		"Sales Invoice"
		if _sepa_line_value(line, "party_type") == "Customer"
		else "Purchase Invoice"
	)

	if invoice_type == "Purchase Invoice" and invoice:
		bill_no = frappe.db.get_value("Purchase Invoice", invoice, "bill_no")
		if bill_no:
			return bill_no

	return invoice


def get_sepa_line_remittance_info(line):
	"""Build SEPA unstructured remittance text (max 140 chars)."""
	document_ref = _sepa_line_value(line, "document_ref")
	invoice = _sepa_line_value(line, "invoice")
	if document_ref and not invoice:
		return document_ref[:140]

	invoice_ref = get_sepa_line_invoice_reference(line)
	return _("Invoice {0}").format(invoice_ref)[:140]


def add_pain_remittance_info(transaction_element, remittance_info):
	"""Add RmtInf/Ustrd to a pain.008 or pain.001 transaction node."""
	if not remittance_info:
		return

	from lxml import etree

	rmt_inf = etree.SubElement(transaction_element, "RmtInf")
	etree.SubElement(rmt_inf, "Ustrd").text = remittance_info


def get_bordereau_line_statuses(bordereau):
	"""Return statuses of invoice lines and manual lines."""
	statuses = [line.status for line in (bordereau.lines or [])]
	statuses.extend(line.status for line in (bordereau.get("manual_lines") or []))
	return statuses


def update_bordereau_status(bordereau_name):
	"""Update bordereau status based on invoice and manual line statuses"""
	bordereau = frappe.get_doc("SEPA Payment Bordereau", bordereau_name)

	statuses = get_bordereau_line_statuses(bordereau)
	if not statuses:
		return

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


def _sepa_line_value(line, field):
	if isinstance(line, dict):
		return line.get(field)
	return getattr(line, field, None)


def get_sepa_payment_type(bordereau):
	return "Receive" if bordereau.payment_type == "Debit" else "Pay"


def get_sepa_party_account(line, company=None):
	invoice = _sepa_line_value(line, "invoice")
	if invoice:
		invoice_type = _sepa_line_value(line, "invoice_type") or (
			"Sales Invoice" if _sepa_line_value(line, "party_type") == "Customer" else "Purchase Invoice"
		)
		account_field = "debit_to" if invoice_type == "Sales Invoice" else "credit_to"
		return frappe.db.get_value(invoice_type, invoice, account_field)

	from erpnext.accounts.party import get_party_account

	return get_party_account(
		_sepa_line_value(line, "party_type"),
		_sepa_line_value(line, "party"),
		company,
	)


def get_sepa_payment_entry_account_fields(bordereau, line, gl_account):
	payment_type = get_sepa_payment_type(bordereau)
	party_account = get_sepa_party_account(line, bordereau.company)

	if not party_account:
		frappe.throw(
			_("No party account found for {0} {1}").format(
				_sepa_line_value(line, "party_type"), _sepa_line_value(line, "party")
			)
		)

	if payment_type == "Pay":
		return payment_type, {"paid_from": gl_account, "paid_to": party_account}

	return payment_type, {"paid_from": party_account, "paid_to": gl_account}


def create_sepa_payment_entry(bordereau, line, gl_account):
	existing_pe = line.get("payment_entry")
	if existing_pe and frappe.db.exists("Payment Entry", existing_pe):
		# Reuse submitted PE; allow recreating after a cancelled (reject) entry
		if frappe.db.get_value("Payment Entry", existing_pe, "docstatus") == 1:
			return existing_pe
		line.payment_entry = None

	remittance_info = get_sepa_line_remittance_info(line)
	invoice_reference = get_sepa_line_invoice_reference(line)
	payment_type, account_fields = get_sepa_payment_entry_account_fields(bordereau, line, gl_account)

	pe_data = {
		"doctype": "Payment Entry",
		"payment_type": payment_type,
		"company": bordereau.company,
		"party_type": line.party_type,
		"party": line.party,
		"paid_amount": line.amount,
		"received_amount": line.amount,
		"posting_date": bordereau.execution_date,
		"reference_no": invoice_reference,
		"reference_date": bordereau.execution_date,
		"remarks": remittance_info,
		"bank_account": bordereau.bank_account,
		**account_fields,
	}
	if frappe.db.has_column("Payment Entry", "sepa_payment_bordereau"):
		pe_data["sepa_payment_bordereau"] = bordereau.name

	payment_entry = frappe.get_doc(pe_data)

	inv_doctype = "Sales Invoice" if line.party_type == "Customer" else "Purchase Invoice"
	invoice_doc = frappe.get_doc(inv_doctype, line.invoice)

	reference = {
		"reference_doctype": inv_doctype,
		"reference_name": line.invoice,
		"allocated_amount": line.amount,
	}

	is_term_based = False
	if invoice_doc.payment_terms_template:
		is_term_based = frappe.db.get_value(
			"Payment Terms Template",
			invoice_doc.payment_terms_template,
			"allocate_payment_based_on_payment_terms",
		)

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

	if frappe.db.has_column("SEPA Payment Bordereau Line", "payment_entry"):
		frappe.db.set_value(
			"SEPA Payment Bordereau Line",
			line.name,
			"payment_entry",
			payment_entry.name,
			update_modified=False,
		)

	if line.mandate and bordereau.payment_type == "Debit":
		mandate = frappe.get_doc("SEPA Mandate", line.mandate)
		if mandate.sequence_type == "FRST":
			mandate.update_to_recurring()

	return payment_entry.name


def create_sepa_manual_line_payment_entry(bordereau, line, gl_account):
	"""Create an unallocated Payment Entry (advance) for a manual SEPA line."""
	existing_pe = line.get("payment_entry")
	if existing_pe and frappe.db.exists("Payment Entry", existing_pe):
		if frappe.db.get_value("Payment Entry", existing_pe, "docstatus") == 1:
			return existing_pe
		line.payment_entry = None

	document_ref = _sepa_line_value(line, "document_ref") or bordereau.name
	payment_type, account_fields = get_sepa_payment_entry_account_fields(bordereau, line, gl_account)

	pe_data = {
		"doctype": "Payment Entry",
		"payment_type": payment_type,
		"company": bordereau.company,
		"party_type": line.party_type,
		"party": line.party,
		"paid_amount": line.amount,
		"received_amount": line.amount,
		"posting_date": bordereau.execution_date,
		"reference_no": document_ref,
		"reference_date": bordereau.execution_date,
		"remarks": document_ref,
		"bank_account": bordereau.bank_account,
		**account_fields,
	}
	if frappe.db.has_column("Payment Entry", "sepa_payment_bordereau"):
		pe_data["sepa_payment_bordereau"] = bordereau.name

	payment_entry = frappe.get_doc(pe_data)
	payment_entry.insert()
	payment_entry.submit()

	return payment_entry.name


def reconcile_sepa_manual_line_on_status_change(bordereau, line, new_status, silent=False):
	if getattr(line, "_reconciled_status_change", False):
		return

	existing_pe = line.get("payment_entry")
	existing_docstatus = None
	if existing_pe and frappe.db.exists("Payment Entry", existing_pe):
		existing_docstatus = frappe.db.get_value("Payment Entry", existing_pe, "docstatus")

	if existing_docstatus == 1:
		line._reconciled_status_change = True
		return

	if existing_docstatus == 2:
		if new_status == "Rejected":
			line._reconciled_status_change = True
			return
		line.payment_entry = None
		frappe.db.set_value(
			"SEPA Payment Bordereau Manual Line",
			line.name,
			"payment_entry",
			None,
			update_modified=False,
		)

	gl_account = frappe.db.get_value("Bank Account", bordereau.bank_account, "account")
	if not gl_account:
		frappe.throw(_("Please link a GL Account to the Bank Account {0}").format(bordereau.bank_account))

	if new_status in ("Accepted", "Rejected"):
		pe_name = create_sepa_manual_line_payment_entry(bordereau, line, gl_account)
		line.payment_entry = pe_name
		frappe.db.set_value(
			"SEPA Payment Bordereau Manual Line",
			line.name,
			"payment_entry",
			pe_name,
			update_modified=False,
		)
		if new_status == "Rejected":
			frappe.get_doc("Payment Entry", pe_name).cancel()
			if not silent:
				frappe.msgprint(
					_("Payment Entry {0} created and cancelled for rejected SEPA line {1} (+ and -)").format(
						pe_name, line.name
					)
				)
		else:
			if not silent:
				frappe.msgprint(_("Payment Entry {0} created for SEPA line {1}").format(pe_name, line.name))
			try:
				create_sepa_bank_transaction(pe_name, bordereau, line)
			except Exception:
				frappe.log_error(
					title=_("SEPA Bank Transaction Creation Error"), message=frappe.get_traceback()
				)

	line._reconciled_status_change = True


def _get_sepa_line_invoice_outstanding(line):
	"""Return outstanding amount for the invoice linked to a SEPA bordereau line."""
	if not line.invoice:
		return 0
	invoice_type = line.invoice_type or (
		"Sales Invoice" if line.party_type == "Customer" else "Purchase Invoice"
	)
	return flt(frappe.db.get_value(invoice_type, line.invoice, "outstanding_amount") or 0)


def reconcile_sepa_line_on_status_change(bordereau, line, new_status, silent=False):
	if getattr(line, "_reconciled_status_change", False):
		return

	existing_pe = line.get("payment_entry")
	existing_docstatus = None
	if existing_pe and frappe.db.exists("Payment Entry", existing_pe):
		existing_docstatus = frappe.db.get_value("Payment Entry", existing_pe, "docstatus")

	# Submitted PE already linked: do not recreate on partial re-validation
	if existing_docstatus == 1:
		line._reconciled_status_change = True
		return

	# Cancelled PE (typical after Reject): clear link so Accept can create a new one
	if existing_docstatus == 2:
		if new_status == "Rejected":
			line._reconciled_status_change = True
			return
		line.payment_entry = None
		frappe.db.set_value(
			"SEPA Payment Bordereau Line",
			line.name,
			"payment_entry",
			None,
			update_modified=False,
		)

	gl_account = frappe.db.get_value("Bank Account", bordereau.bank_account, "account")
	if not gl_account:
		frappe.throw(_("Please link a GL Account to the Bank Account {0}").format(bordereau.bank_account))

	if new_status == "Accepted":
		outstanding = _get_sepa_line_invoice_outstanding(line)
		if flt(outstanding) <= 0:
			# Invoice already settled (external payment / previous PE): close the line without PE
			if not silent:
				frappe.msgprint(
					_(
						"Invoice {0} has no outstanding amount; SEPA line {1} marked as accepted without Payment Entry"
					).format(line.invoice, line.name)
				)
			line._reconciled_status_change = True
			return

		pe_name = create_sepa_payment_entry(bordereau, line, gl_account)
		line.payment_entry = pe_name
		if not silent:
			frappe.msgprint(_("Payment Entry {0} created for SEPA line {1}").format(pe_name, line.name))

		# Création de la transaction bancaire associée
		try:
			bt_name = create_sepa_bank_transaction(pe_name, bordereau, line)
			if bt_name and not silent:
				frappe.msgprint(
					_("Bank Transaction {0} created for SEPA line {1}").format(bt_name, line.name)
				)
		except Exception:
			frappe.log_error(title=_("SEPA Bank Transaction Creation Error"), message=frappe.get_traceback())

	elif new_status == "Rejected":
		outstanding = _get_sepa_line_invoice_outstanding(line)
		if flt(outstanding) <= 0:
			# Already paid: no +/- Payment Entry pair to create
			if not silent:
				frappe.msgprint(
					_(
						"Invoice {0} has no outstanding amount; SEPA line {1} marked as rejected without Payment Entry"
					).format(line.invoice, line.name)
				)
			line._reconciled_status_change = True
			return

		pe_name = create_sepa_payment_entry(bordereau, line, gl_account)
		line.payment_entry = pe_name
		pe_doc = frappe.get_doc("Payment Entry", pe_name)
		pe_doc.cancel()
		if not silent:
			frappe.msgprint(
				_("Payment Entry {0} created and cancelled for rejected SEPA line {1} (+ and -)").format(
					pe_name, line.name
				)
			)

	line._reconciled_status_change = True


def create_sepa_bank_transaction(pe_name, bordereau, line):
	doc = frappe.get_doc("Payment Entry", pe_name)

	if doc.payment_type not in ("Receive", "Pay"):
		return

	bank_account = doc.bank_account or bordereau.bank_account
	payment_amount = doc.paid_amount

	if not bank_account:
		return

	gl_account = doc.paid_to if doc.payment_type == "Receive" else doc.paid_from
	is_bank = frappe.db.get_value("Account", gl_account, "account_type") == "Bank"
	if not is_bank:
		return

	bt_exists = frappe.db.exists("Bank Transaction", {"reference_number": doc.name, "company": doc.company})
	if bt_exists:
		return

	bt = frappe.new_doc("Bank Transaction")

	bt.date = doc.posting_date or bordereau.execution_date
	bt.bank_account = bank_account
	bt.company = doc.company

	if doc.payment_type == "Receive":
		bt.deposit = payment_amount
		bt.withdrawal = 0.0
		bt.currency = doc.paid_to_account_currency
	else:
		bt.withdrawal = payment_amount
		bt.deposit = 0.0
		bt.currency = doc.paid_from_account_currency

	bt.reference_number = doc.name
	bt.party_type = doc.party_type
	bt.party = doc.party
	bt.description = doc.remarks or get_sepa_line_remittance_info(line)

	bt.insert(ignore_permissions=True)

	if getattr(bt, "docstatus", 0) == 0 and frappe.get_meta("Bank Transaction").is_submittable:
		bt.submit()

	return bt.name
