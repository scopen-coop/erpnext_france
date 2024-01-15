# Copyright (c) 2020, Dokos SAS and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff, flt, getdate, month_diff, nowdate

from erpnext.accounts.report.financial_statements import get_columns, get_period_list
from erpnext.accounts.utils import get_currency_precision

PERIOD_MAP = {"Month": "Monthly", "Year": "Yearly"}


def execute(filters=None):
	period_list = get_period_list(
		filters.from_fiscal_year,
		filters.to_fiscal_year,
		filters.period_start_date,
		filters.period_end_date,
		filters.filter_based_on,
		filters.periodicity,
		company=filters.company,
	)

	data = get_data(filters, period_list)
	columns = get_columns(
		filters.periodicity, period_list, filters.accumulated_values, company=filters.company
	)
	columns = [x for x in columns if x.get("fieldname") != "account"]
	for column in columns:
		if column["fieldname"] == "total":
			column["label"] = _("Average")

	columns.insert(
		0,
		{
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 500,
			"label": _("Customer"),
		},
	)
	return columns, data, [], get_chart_data(columns, data)


def get_data(filters, period_list):
	invoices = frappe.get_all(
		"Sales Invoice",
		filters={
			# "posting_date": ("between", (filters.period_start_date, filters.period_end_date)),
			"subscription": ("is", "set"),
			"docstatus": 1,
		},
		fields=["name", "subscription", "customer", "total", "posting_date", "from_date", "to_date"],
	)

	subscriptions = frappe.get_all(
		"Subscription",
		filters={"status": ("!=", "Cancelled")},
		fields=[
			"name",
			"customer",
			"total",
			"recurrence_period",
			"current_invoice_start",
			"current_invoice_end",
		],
	)

	filtered_invoices = []
	for subscription in subscriptions:
		filtered_invoices.extend([x for x in invoices if x.subscription == subscription.name])

	customers = list(
		set([x.customer for x in filtered_invoices] + [x.customer for x in subscriptions])
	)

	result = []
	precision = get_currency_precision() or 2
	total_row = {x.key: 0 for x in period_list if x.key != "total"}
	total_row.update({"customer": _("Total"), "total": 0})
	for customer in customers:
		customer_total = 0
		average_count = 0
		row = {
			"customer": customer,
			"currency": frappe.get_cached_value("Company", filters.company, "default_currency"),
		}
		for index, period in enumerate(period_list):
			total = get_invoices_mrr([x for x in filtered_invoices if x.customer == customer], period)
			customer_subscriptions = [x for x in subscriptions if x.customer == customer]
			if not total and period.to_date >= getdate(nowdate()):
				total = get_subscription_mrr(customer_subscriptions, period)

			customer_total += total
			total_row[period.key] += total

			if total:
				average_count += 1

			row.update({period.key: flt(total, precision)})

		average_total = flt(customer_total, precision) / flt(average_count or 1)
		total_row["total"] += average_total
		row.update({"total": average_total})
		result.append(row)

	result.sort(key=lambda x: x["total"], reverse=True)

	result.append(total_row)
	return result


def get_invoices_mrr(invoices, period):
	total = 0.0
	for invoice in invoices:
		if invoice.from_date and invoice.to_date:
			if (
				getdate(period.from_date).replace(day=1) >= getdate(invoice.from_date).replace(day=1)
				and getdate(period.to_date).replace(day=1) <= getdate(invoice.to_date).replace(day=1)
				and monthdelta(invoice.from_date, invoice.to_date) + 1 > 1
			):
				return flt(invoice.total) / (monthdelta(invoice.from_date, invoice.to_date) + 1)

			elif period.to_date >= getdate(invoice.posting_date) >= period.from_date and getdate(
				period.to_date
			) >= getdate(invoice.from_date):
				total += flt(invoice.total)

	return total


def monthdelta(d1, d2):
	from calendar import monthrange
	from datetime import timedelta

	delta = 0
	while True:
		mdays = monthrange(d1.year, d1.month)[1]
		d1 += timedelta(days=mdays)
		if d1 <= d2:
			delta += 1
		else:
			break
	return delta


def get_subscription_mrr(subscriptions, period):
	month_total = 0
	for subscription in subscriptions:
		recurrence_period = frappe.get_cached_value(
			"Recurrence Period",
			subscription.recurrence_period,
			["billing_interval", "billing_interval_count"],
			as_dict=True,
		)

		if not recurrence_period:
			continue

		subscription_total = flt(subscription.total) / flt(recurrence_period.billing_interval_count)

		if recurrence_period.billing_interval == "Month":
			month_total += subscription_total

		elif recurrence_period.billing_interval == "Year":
			month_total += subscription_total / 12

		elif recurrence_period.billing_interval == "Day":
			month_total += subscription_total * date_diff(period.to_date, period.from_date)

		elif recurrence_period.billing_interval == "Week":
			month_total += subscription_total * date_diff(period.to_date, period.from_date) / 7

	return month_total * month_diff(period.to_date, period.from_date)


def get_chart_data(columns, data):
	values = []
	precision = get_currency_precision() or 2
	for p in columns[3:]:
		if p.get("fieldname") != "total":
			values.append(flt(data[-1].get(p.get("fieldname")), precision))

	chart = {
		"data": {
			"labels": [d.get("label") for d in columns[3:] if d.get("fieldname") != "total"],
			"datasets": [{"name": _("Monthly Recurring Revenue"), "values": values}],
		},
		"type": "line",
		"colors": ["#ffa00a"],
		"lineOptions": {"regionFill": 1},
	}

	return chart
