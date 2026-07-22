# Copyright (c) 2026, Scopen and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, get_datetime


def execute():
	"""Backfill Payment Entry <-> SEPA Payment Bordereau links for existing documents.

	Runs in post_model_sync, before fixtures sync, so the Payment Entry custom field
	may not exist yet — create it here when missing.
	"""
	_ensure_payment_entry_sepa_field()

	if not frappe.db.has_column("Payment Entry", "sepa_payment_bordereau"):
		return
	if not frappe.db.has_column("SEPA Payment Bordereau Line", "payment_entry"):
		return

	lines = frappe.get_all(
		"SEPA Payment Bordereau Line",
		filters={
			"status": ("in", ("Accepted", "Rejected")),
			"payment_entry": ("is", "not set"),
		},
		fields=["name", "parent", "invoice", "invoice_type", "amount", "modified"],
	)

	for line in lines:
		invoice_type = line.invoice_type or "Sales Invoice"
		pe_refs = frappe.get_all(
			"Payment Entry Reference",
			filters={
				"reference_doctype": invoice_type,
				"reference_name": line.invoice,
			},
			fields=["parent", "allocated_amount"],
		)
		if not pe_refs:
			continue

		candidates = []
		for ref in pe_refs:
			pe = frappe.db.get_value(
				"Payment Entry",
				ref.parent,
				["name", "paid_amount", "sepa_payment_bordereau", "creation"],
				as_dict=True,
			)
			if not pe:
				continue
			if pe.sepa_payment_bordereau and pe.sepa_payment_bordereau != line.parent:
				continue
			if (
				abs(flt(pe.paid_amount) - flt(line.amount)) > 0.01
				and abs(flt(ref.allocated_amount) - flt(line.amount)) > 0.01
			):
				continue
			candidates.append(pe)

		if not candidates:
			continue

		# Prefer already linked PE, else the closest by creation time to the line modification
		linked = [c for c in candidates if c.sepa_payment_bordereau == line.parent]
		if linked:
			pe = linked[0]
		else:
			line_modified = get_datetime(line.modified)
			candidates.sort(key=lambda c: abs((get_datetime(c.creation) - line_modified).total_seconds()))
			pe = candidates[0]

		frappe.db.set_value(
			"Payment Entry",
			pe.name,
			"sepa_payment_bordereau",
			line.parent,
			update_modified=False,
		)
		frappe.db.set_value(
			"SEPA Payment Bordereau Line",
			line.name,
			"payment_entry",
			pe.name,
			update_modified=False,
		)


def _ensure_payment_entry_sepa_field():
	if frappe.db.exists("Custom Field", "Payment Entry-sepa_payment_bordereau"):
		return

	frappe.get_doc(
		{
			"doctype": "Custom Field",
			"dt": "Payment Entry",
			"fieldname": "sepa_payment_bordereau",
			"fieldtype": "Link",
			"label": "SEPA Payment Bordereau",
			"options": "SEPA Payment Bordereau",
			"insert_after": "accounting_journal",
			"read_only": 1,
			"allow_on_submit": 1,
			"no_copy": 1,
			"in_standard_filter": 1,
			"module": "ERPNext France",
		}
	).insert(ignore_permissions=True)
