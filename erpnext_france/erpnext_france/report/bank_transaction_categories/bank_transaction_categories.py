# Copyright (c) 2022, Dokos SAS and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	chart_data = get_chart_data(data)
	return columns, data, None, chart_data


def get_columns(filters=None):
	return [
		{"fieldtype": "Data", "fieldname": "category", "label": _("Category"), "width": 250},
		{"fieldtype": "Currency", "fieldname": "amount", "label": _("Amount"), "width": 300},
	]


def get_data(filters=None):
	return frappe.get_list(
		"Bank Transaction",
		filters={
			"date": ("Timespan", filters["period"]),
			"company": filters["company"],
			filters.get("transaction_type"): (">", 0.0),
		},
		fields=["category", f'sum({filters.get("transaction_type")}) as amount'],
		group_by="category",
	)


def get_chart_data(data):
	return {
		"data": {
			"labels": [d.category or _("Without category") for d in data],
			"datasets": [{"name": "Amount", "values": [d.amount for d in data]}],
		},
		"type": "pie",
		"height": 500,
		"fieldtype": "Currency",
	}
