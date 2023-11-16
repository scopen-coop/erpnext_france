# Copyright (c) 2021, Dokos SAS and Contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.utils import flt

from erpnext.accounts.report.balance_sheet.balance_sheet import check_opening_balance
from erpnext.accounts.report.financial_statements import (
	accumulate_values_into_parents,
	add_total_row,
	filter_out_zero_value_rows,
	get_appropriate_currency,
	get_period_list,
	set_gl_entries_by_account,
	sort_accounts,
)

DEPRECIATION_ACCOUNT_TYPES = ["Accumulated Depreciation", "Depreciation"]


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

	additional_columns = []
	for index, period in enumerate(period_list):
		if index == len(period_list) - 1:
			for period_type in ["depreciation", "gross"]:
				additional_period = period.copy()
				additional_period.key = additional_period.key + "_" + period_type
				additional_period["type"] = period_type
				additional_period["label"] = (
					additional_period.label + " " + _("- Gross")
					if period_type == "gross"
					else _("Amortization - Depreciation")
				)
				additional_columns.append(additional_period)
		period["type"] = "net"
		period["label"] = period.label + " " + _(" - Net")
	period_list.extend(additional_columns)
	period_list = list(reversed(sorted(period_list, key=lambda x: x["from_date"])))

	filters.period_start_date = period_list[0]["year_start_date"]

	currency = filters.presentation_currency or frappe.get_cached_value(
		"Company", filters.company, "default_currency"
	)

	asset = get_data(
		filters.company,
		"Asset",
		"Debit",
		period_list,
		only_current_fiscal_year=False,
		filters=filters,
		accumulated_values=filters.accumulated_values,
	)

	liability = get_data(
		filters.company,
		"Liability",
		"Credit",
		period_list,
		only_current_fiscal_year=False,
		filters=filters,
		accumulated_values=filters.accumulated_values,
	)

	equity = get_data(
		filters.company,
		"Equity",
		"Credit",
		period_list,
		only_current_fiscal_year=False,
		filters=filters,
		accumulated_values=filters.accumulated_values,
	)

	provisional_profit_loss, total_credit = get_provisional_profit_loss(
		asset, liability, equity, period_list, filters.company, currency
	)

	message, opening_balance = check_opening_balance(asset, liability, equity)

	data = []
	data.extend(asset or [])
	data.extend(equity or [])
	data.extend(liability or [])
	if opening_balance and round(opening_balance, 2) != 0:
		unclosed = {
			"account_name": "'" + _("Unclosed Fiscal Years Profit / Loss (Credit)") + "'",
			"account": "'" + _("Unclosed Fiscal Years Profit / Loss (Credit)") + "'",
			"warn_if_negative": True,
			"currency": currency,
		}
		for period in period_list:
			unclosed[period.key] = opening_balance
			if provisional_profit_loss:
				provisional_profit_loss[period.key] = provisional_profit_loss[period.key] - opening_balance

		unclosed["total"] = opening_balance
		data.append(unclosed)

	if provisional_profit_loss:
		data.append(provisional_profit_loss)
	if total_credit:
		data.append(total_credit)

	columns = get_columns(
		filters.periodicity, period_list, filters.accumulated_values, company=filters.company
	)

	chart = get_chart_data(filters, columns, asset, liability, equity)

	report_summary = get_report_summary(
		period_list, asset, liability, equity, provisional_profit_loss, currency, filters
	)

	return columns, data, message, chart, report_summary


def get_data(
	company,
	root_type,
	balance_must_be,
	period_list,
	filters=None,
	accumulated_values=1,
	only_current_fiscal_year=True,
	ignore_closing_entries=False,
	ignore_accumulated_values_for_fy=False,
	total=True,
):
	root_type_query = (
		f"root_type='{root_type}'"
		if root_type not in ("Asset", "Liability")
		else "root_type in ('Asset', 'Liability')"
	)

	accounts = get_accounts(company, root_type_query)
	if not accounts:
		return None

	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)

	company_currency = get_appropriate_currency(company, filters)

	gl_entries_by_account = {}
	for root in frappe.db.sql(
		"""select lft, rgt from tabAccount
			where {0} and ifnull(parent_account, '') = ''""".format(
			root_type_query
		),
		as_dict=1,
	):

		set_gl_entries_by_account(
			company,
			period_list[-1]["year_start_date"] if only_current_fiscal_year else None,
			period_list[0]["to_date"],
			root.lft,
			root.rgt,
			filters,
			gl_entries_by_account,
			ignore_closing_entries=ignore_closing_entries,
		)

	calculate_values(
		accounts_by_name,
		gl_entries_by_account,
		period_list,
		accumulated_values,
		ignore_accumulated_values_for_fy,
	)

	if root_type in ("Asset", "Liability"):
		accounts = filter_accounts_by_root_type(
			accounts, accounts_by_name, parent_children_map, root_type, balance_must_be, period_list
		)

	accounts = sorted([x for x in accounts if x.root_type == root_type], key=lambda x: x["lft"])

	accumulate_values_into_parents(accounts, accounts_by_name, period_list)
	out = prepare_data(accounts, balance_must_be, period_list, company_currency)
	out = filter_out_zero_value_rows(out, parent_children_map)

	if out and total:
		add_total_row(out, root_type, balance_must_be, period_list, company_currency)

	return out


def filter_accounts_by_root_type(
	accounts, accounts_by_name, parent_children_map, root_type, balance_must_be, period_list
):
	for account in accounts:
		for period in period_list:
			if account.account_type in DEPRECIATION_ACCOUNT_TYPES or account.negative_in_balance_sheet:
				continue

			if (
				account.root_type == root_type
				and account.get(period.key)
				and account.balance_sheet_alternative_category
			):
				if (
					flt(account.get(period.key, 0)) > 0
					if balance_must_be == "Credit"
					else flt(account.get(period.key, 0)) < 0
				):
					account[period.key] = 0
					account["opening_balance"] = 0
			elif (
				account.root_type != root_type
				and account.get(period.key)
				and account.balance_sheet_alternative_category
			):
				if (
					flt(account.get(period.key, 0)) < 0
					if balance_must_be == "Credit"
					else flt(account.get(period.key, 0)) > 0
				):
					parent_children_map[account.balance_sheet_alternative_category].append(account)
					account["root_type"] = root_type
					account["parent_account"] = account.balance_sheet_alternative_category
					account["lft"] = (
						flt(accounts_by_name.get(account.balance_sheet_alternative_category).get("lft")) + 1.0
					)
					account["indent"] = (
						flt(accounts_by_name.get(account.balance_sheet_alternative_category).get("indent")) + 1.0
					)
				else:
					account[period.key] = 0
					account["opening_balance"] = 0

	return accounts


def get_accounts(company, root_type):
	return frappe.db.sql(
		"""
		select name, account_number, parent_account, lft, rgt, root_type, report_type,
		account_name, include_in_gross, account_type, is_group, lft, rgt, do_not_show_account_number,
		negative_in_balance_sheet, balance_sheet_alternative_category
		from `tabAccount`
		where company=%s and {0} order by lft""".format(
			root_type
		),
		company,
		as_dict=True,
	)


def filter_accounts(accounts, depth=10):
	parent_children_map = {}
	accounts_by_name = {}
	for d in accounts:
		accounts_by_name[d.name] = d
		parent_children_map.setdefault(d.parent_account or None, []).append(d)

	filtered_accounts = []

	def add_to_list(parent, level):
		if level < depth:
			children = parent_children_map.get(parent) or []
			sort_accounts(children, is_root=True if parent == None else False)

			for child in children:
				child.indent = level
				filtered_accounts.append(child)
				add_to_list(child.name, level + 1)

	add_to_list(None, 0)

	return filtered_accounts, accounts_by_name, parent_children_map


def calculate_values(
	accounts_by_name,
	gl_entries_by_account,
	period_list,
	accumulated_values,
	ignore_accumulated_values_for_fy,
):
	for entries in iter(gl_entries_by_account.values()):
		for entry in entries:
			d = accounts_by_name.get(entry.account)
			if not d:
				frappe.msgprint(
					_("Could not retrieve information for {0}.").format(entry.account),
					title="Error",
					raise_exception=1,
				)
			for period in period_list:
				# check if posting date is within the period

				if period.type == "gross" and d.account_type in DEPRECIATION_ACCOUNT_TYPES:
					continue

				if period.type == "depreciation" and d.account_type not in DEPRECIATION_ACCOUNT_TYPES:
					continue

				if entry.posting_date <= period.to_date:
					if (accumulated_values or entry.posting_date >= period.from_date) and (
						not ignore_accumulated_values_for_fy or entry.fiscal_year == period.to_date_fiscal_year
					):
						d[period.key] = d.get(period.key, 0.0) + flt(entry.debit) - flt(entry.credit)

			if entry.posting_date < period_list[0].year_start_date:
				d["opening_balance"] = d.get("opening_balance", 0.0) + flt(entry.debit) - flt(entry.credit)


def prepare_data(accounts, balance_must_be, period_list, company_currency):
	data = []
	year_start_date = period_list[0]["year_start_date"].strftime("%Y-%m-%d")
	year_end_date = period_list[-1]["year_end_date"].strftime("%Y-%m-%d")

	for d in accounts:
		# add to output
		has_value = False
		total = 0
		row = frappe._dict(
			{
				"account": _(d.name),
				"account_number": d.account_number,
				"parent_account": _(d.parent_account) if d.parent_account else "",
				"indent": flt(d.indent),
				"year_start_date": year_start_date,
				"year_end_date": year_end_date,
				"currency": company_currency,
				"include_in_gross": d.include_in_gross,
				"account_type": d.account_type,
				"is_group": d.is_group,
				"opening_balance": d.get("opening_balance", 0.0) * (1 if balance_must_be == "Debit" else -1),
				"account_name": (
					"%s - %s" % (_(d.account_number), _(d.account_name))
					if d.account_number and not d.do_not_show_account_number
					else _(d.account_name)
				),
			}
		)
		for period in period_list:
			if (d.get(period.key) and balance_must_be == "Credit") or (
				d.get(period.key) and period.type == "depreciation"
			):
				# change sign based on Debit or Credit, since calculation is done using (debit - credit)
				d[period.key] *= -1

			row[period.key] = flt(d.get(period.key, 0.0), 3)

			if abs(row[period.key]) >= 0.005:
				# ignore zero values
				has_value = True
				total += flt(row[period.key])

		row["has_value"] = has_value
		row["total"] = total
		data.append(row)

	return data


def get_provisional_profit_loss(
	asset, liability, equity, period_list, company, currency=None, consolidated=False
):
	provisional_profit_loss = {}
	total_row = {}
	if asset and (liability or equity):
		total = total_row_total = 0
		currency = currency or frappe.get_cached_value("Company", company, "default_currency")
		total_row = {
			"account_name": "'" + _("Total (Credit)") + "'",
			"account": "'" + _("Total (Credit)") + "'",
			"warn_if_negative": True,
			"currency": currency,
		}
		has_value = False

		for period in period_list:
			key = period if consolidated else period.key
			effective_liability = 0.0
			if liability:
				effective_liability += flt(liability[-2].get(key))
			if equity:
				effective_liability += flt(equity[-2].get(key))

			calculated_profit_loss = flt(asset[-2].get(key)) - effective_liability
			provisional_profit_loss[key] = calculated_profit_loss if period.type == "net" else 0.0
			total_row[key] = (
				effective_liability + calculated_profit_loss if period.type != "depreciation" else 0.0
			)

			if calculated_profit_loss:
				has_value = True

			total += flt(calculated_profit_loss)
			provisional_profit_loss["total"] = total

			total_row_total += flt(total_row[key])
			total_row["total"] = total_row_total

		if has_value:
			provisional_profit_loss.update(
				{
					"account_name": "'" + _("Provisional Profit / Loss (Credit)") + "'",
					"account": "'" + _("Provisional Profit / Loss (Credit)") + "'",
					"warn_if_negative": True,
					"currency": currency,
				}
			)

	return provisional_profit_loss, total_row


def get_report_summary(
	period_list,
	asset,
	liability,
	equity,
	provisional_profit_loss,
	currency,
	filters,
	consolidated=False,
):

	net_asset, net_liability, net_equity, net_provisional_profit_loss = 0.0, 0.0, 0.0, 0.0

	if filters.get("accumulated_values"):
		period_list = [period_list[-1]]

	for period in period_list:
		if period.type != "net":
			continue

		key = period if consolidated else period.key
		if asset:
			net_asset += asset[-2].get(key)
		if liability:
			net_liability += liability[-2].get(key)
		if equity:
			net_equity += equity[-2].get(key)
		if provisional_profit_loss:
			net_provisional_profit_loss += provisional_profit_loss.get(key)

	return [
		{
			"value": net_asset,
			"label": _("Total Asset"),
			"indicator": "Green",
			"datatype": "Currency",
			"currency": currency,
		},
		{
			"value": net_liability,
			"label": _("Total Liability"),
			"datatype": "Currency",
			"indicator": "Red",
			"currency": currency,
		},
		{
			"value": net_equity,
			"label": _("Total Equity"),
			"datatype": "Currency",
			"indicator": "Blue",
			"currency": currency,
		},
		{
			"value": net_provisional_profit_loss,
			"label": _("Provisional Profit / Loss (Credit)"),
			"indicator": "Green" if net_provisional_profit_loss > 0 else "Red",
			"datatype": "Currency",
			"currency": currency,
		},
	]


def get_chart_data(filters, columns, asset, liability, equity):
	labels = [d.get("label") for d in columns[3:] if d.get("period_type") == "net"]

	asset_data, liability_data, equity_data = [], [], []

	for p in columns[3:]:
		if p.get("period_type") == "net":
			if asset:
				asset_data.append(asset[-2].get(p.get("fieldname")))
			if liability:
				liability_data.append(liability[-2].get(p.get("fieldname")))
			if equity:
				equity_data.append(equity[-2].get(p.get("fieldname")))

	datasets = []
	if asset_data:
		datasets.append({"name": _("Assets"), "values": asset_data})
	if liability_data:
		datasets.append({"name": _("Liabilities"), "values": liability_data})
	if equity_data:
		datasets.append({"name": _("Equity"), "values": equity_data})

	chart = {"data": {"labels": labels, "datasets": datasets}}

	if not filters.accumulated_values:
		chart["type"] = "bar"
	else:
		chart["type"] = "line"

	return chart


def get_columns(periodicity, period_list, accumulated_values=1, company=None):
	columns = [
		{
			"fieldname": "account",
			"label": _("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 500,
		},
		{
			"fieldname": "account_number",
			"label": _("Account Number"),
			"fieldtype": "Data",
			"width": 120,
			"hidden": 1,
		},
	]
	if company:
		columns.append(
			{
				"fieldname": "currency",
				"label": _("Currency"),
				"fieldtype": "Link",
				"options": "Currency",
				"hidden": 1,
			}
		)
	for period in period_list:
		columns.append(
			{
				"fieldname": period.key,
				"label": period.label,
				"fieldtype": "Currency",
				"options": "currency",
				"width": 150,
				"period_type": period.type,
			}
		)
	if periodicity != "Yearly":
		if not accumulated_values:
			columns.append(
				{"fieldname": "total", "label": _("Total"), "fieldtype": "Currency", "width": 150}
			)

	return columns
