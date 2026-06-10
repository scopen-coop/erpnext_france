# Copyright (c) 2026, Scopen and contributors
# For license information, please see license.txt

import frappe


def execute():
	if not frappe.db.has_column("Sales Invoice", "sepa_payment_bordereau"):
		return

	from erpnext_france.regional.france.sepa_utils import sync_invoice_sepa_bordereau_link

	for row in frappe.get_all(
		"SEPA Payment Bordereau Line",
		filters={"invoice_type": "Sales Invoice"},
		fields=["invoice"],
		distinct=True,
	):
		sync_invoice_sepa_bordereau_link(row.invoice, "Sales Invoice")
