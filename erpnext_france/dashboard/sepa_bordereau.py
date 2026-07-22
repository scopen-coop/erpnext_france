# Copyright (c) 2026, Scopen and contributors
# For license information, please see license.txt

from frappe import _

SEPA_BORDEREAU = "SEPA Payment Bordereau"


def add_sepa_bordereau_connection(data, invoice_type):
	"""Link SEPA Payment Bordereau in invoice connections without the create (+) button.

	Uses internal_links to hide the + button. When the denormalized field is empty
	(or missing on Purchase Invoice), get_open_count falls back to an external query
	on SEPA Payment Bordereau Line.invoice.
	"""
	data.setdefault("internal_links", {})
	data["internal_links"][SEPA_BORDEREAU] = "sepa_payment_bordereau"

	data.setdefault("non_standard_fieldnames", {})
	data["non_standard_fieldnames"][SEPA_BORDEREAU] = "invoice"

	data.setdefault("dynamic_links", {})
	data["dynamic_links"]["invoice"] = [invoice_type, "invoice_type"]

	_append_to_payment_transactions(data)
	return data


def _append_to_payment_transactions(data):
	transactions = data.setdefault("transactions", [])
	for group in transactions:
		items = group.get("items") or []
		if "Payment Entry" in items or group.get("label") == _("Payment"):
			if SEPA_BORDEREAU not in items:
				items.append(SEPA_BORDEREAU)
			return

	transactions.append({"label": _("Payment"), "items": [SEPA_BORDEREAU]})
