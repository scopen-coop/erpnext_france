# Copyright (c) 2026, Scopen and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.utils import flt

PRESENTATION_CHILD_DOCTYPES = ("Quotation Item", "Sales Order Item", "Sales Invoice Item")
PRESENTATION_PARENT_DOCTYPES = ("Quotation", "Sales Order", "Sales Invoice")

ZERO_FIELDS = (
	"qty",
	"stock_qty",
	"rate",
	"amount",
	"net_amount",
	"net_rate",
	"base_rate",
	"base_amount",
	"base_net_amount",
	"base_net_rate",
	"price_list_rate",
	"base_price_list_rate",
	"discount_amount",
	"discount_percentage",
	"margin_rate_or_amount",
)


# ---------------------------------------------------------------------------
# Doc events
# ---------------------------------------------------------------------------
def before_validate(doc, method=None):
	"""Force qty/rate/amount = 0 on presentation rows BEFORE ERPNext's
	validate runs (otherwise calculate_taxes_and_totals would recompute
	them from qty*rate)."""
	if not getattr(doc, "items", None):
		return

	for row in doc.items:
		if not row.get("is_presentation_line"):
			continue

		for f in ZERO_FIELDS:
			if hasattr(row, f):
				row.set(f, 0)

		row.margin_type = ""

		# Make sure something readable lives in item_name (used by ERPNext
		# for display and required by some downstream code paths).
		label = row.get("section_label") or row.get("display_type") or "Presentation Line"
		row.item_name = label
		if not row.get("description"):
			row.description = label


def validate(doc, method=None):
	"""Recompute subtotal_amount on Subtotal rows. Runs AFTER ERPNext's
	validate, so item amounts are final."""
	if not getattr(doc, "items", None):
		return

	running_total = 0.0
	for row in doc.items:
		if row.get("is_presentation_line"):
			if row.get("display_type") == "Subtotal":
				row.subtotal_amount = flt(running_total)
				running_total = 0.0
			continue
		running_total += flt(row.get("amount") or 0.0)


# ---------------------------------------------------------------------------
# Setup (Custom Fields + Property Setters), idempotent
# ---------------------------------------------------------------------------
def _custom_fields_definition():
	fields = {}
	for dt in PRESENTATION_CHILD_DOCTYPES:
		fields[dt] = [
			{
				"fieldname": "is_presentation_line",
				"label": "Is Presentation Line",
				"fieldtype": "Check",
				"insert_after": "item_code",
				"default": "0",
				"in_list_view": 0,
				"print_hide": 1,
				"no_copy": 0,
				"translatable": 0,
			},
			{
				"fieldname": "display_type",
				"label": "Display Type",
				"fieldtype": "Select",
				"options": "\nSection\nNote\nSubtotal",
				"insert_after": "is_presentation_line",
				"depends_on": "eval:doc.is_presentation_line",
				"in_list_view": 0,
				"print_hide": 1,
				"translatable": 0,
			},
			{
				"fieldname": "section_label",
				"label": "Section / Note Label",
				"fieldtype": "Data",
				"insert_after": "display_type",
				"depends_on": (
					'eval:doc.is_presentation_line && '
					'(doc.display_type=="Section" || doc.display_type=="Note")'
				),
				"in_list_view": 0,
				"print_hide": 1,
				"translatable": 1,
			},
			{
				"fieldname": "subtotal_amount",
				"label": "Subtotal Amount",
				"fieldtype": "Currency",
				"insert_after": "section_label",
				"depends_on": 'eval:doc.is_presentation_line && doc.display_type=="Subtotal"',
				"options": "currency",
				"read_only": 1,
				"print_hide": 1,
			},
		]
	return fields


def _property_setters_definition():
	"""Relax `item_code` mandatory only for presentation rows.
	`reqd=0` so server-side _validate_mandatory does not enforce blindly,
	then `mandatory_depends_on` re-enforces it for normal product rows."""
	specs = []
	for dt in PRESENTATION_CHILD_DOCTYPES:
		specs.append(
			dict(
				doctype=dt,
				fieldname="item_code",
				property="reqd",
				value="0",
				property_type="Check",
			)
		)
		specs.append(
			dict(
				doctype=dt,
				fieldname="item_code",
				property="mandatory_depends_on",
				value="eval:!doc.is_presentation_line",
				property_type="Data",
			)
		)
	return specs


def setup_presentation_lines():
	"""Idempotent. Called from after_migrate."""
	create_custom_fields(_custom_fields_definition(), update=True)

	for ps in _property_setters_definition():
		make_property_setter(
			doctype=ps["doctype"],
			fieldname=ps["fieldname"],
			property=ps["property"],
			value=ps["value"],
			property_type=ps["property_type"],
			validate_fields_for_doctype=False,
		)

	frappe.db.commit()
