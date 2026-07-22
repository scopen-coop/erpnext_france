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

	_append_sepa_to_transactions(
		data,
		preferred_items=("Payment Entry",),
		preferred_labels=(_("Payment"),),
		fallback_label=_("Payment"),
	)
	return data


def add_sepa_bordereau_connection_for_payment_entry(data):
	"""Link SEPA Payment Bordereau in Payment Entry connections without the create (+) button."""
	data.setdefault("internal_links", {})
	data["internal_links"][SEPA_BORDEREAU] = "sepa_payment_bordereau"

	data.setdefault("non_standard_fieldnames", {})
	data["non_standard_fieldnames"][SEPA_BORDEREAU] = "payment_entry"

	_append_sepa_to_transactions(
		data,
		preferred_items=("Bank Transaction",),
		preferred_labels=(_("Reference"), _("SEPA")),
		fallback_label=_("SEPA"),
	)
	return data


def _append_sepa_to_transactions(data, preferred_items=(), preferred_labels=(), fallback_label=None):
	transactions = data.setdefault("transactions", [])
	for group in transactions:
		items = group.get("items") or []
		if any(item in items for item in preferred_items) or group.get("label") in preferred_labels:
			if SEPA_BORDEREAU not in items:
				items.append(SEPA_BORDEREAU)
			return

	transactions.append({"label": fallback_label or _("SEPA"), "items": [SEPA_BORDEREAU]})
