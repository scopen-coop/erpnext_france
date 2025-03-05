# Copyright (c) 2024, Scopen.fr
# License: GNU General Public License v3. See license.txt

import json
import os

import frappe
from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import (
	get_account_tree_from_existing_company,
	get_chart,
	get_charts_for_country,
)


@frappe.whitelist()
def get_charts_for_fr(country, with_standard=False):
	charts = []

	def _get_chart_name(content):
		if content:
			content = json.loads(content)
			if (
				content and content.get("disabled", "No") == "No"
			) or frappe.local.flags.allow_unverified_charts:
				charts.append(content["name"])

	country_code = frappe.get_cached_value("Country", country, "code")
	if country_code == "fr":
		path = frappe.get_app_path("erpnext_france", "regional", "france", "chart_of_accounts")
		if not os.path.exists(path):
			return charts

		for fname in os.listdir(path):
			fname = frappe.as_unicode(fname)
			if (fname.startswith(country_code) or fname.startswith(country)) and fname.endswith(".json"):
				with open(os.path.join(path, fname)) as f:
					_get_chart_name(f.read())
	else:
		return get_charts_for_country(country, with_standard)

	# if more than one charts, returned then add the standard
	if len(charts) != 1 or with_standard:
		charts += ["Standard", "Standard with Numbers"]

	return charts


@frappe.whitelist()
def get_chart_fr(chart_template, existing_company=None):
	chart = get_chart(chart_template, existing_company)
	if chart == {} or chart is None:
		if existing_company:
			return get_account_tree_from_existing_company(existing_company)

		elif chart_template == "Standard":
			from erpnext.accounts.doctype.account.chart_of_accounts.verified import (
				standard_chart_of_accounts,
			)

			return standard_chart_of_accounts.get()
		elif chart_template == "Standard with Numbers":
			from erpnext.accounts.doctype.account.chart_of_accounts.verified import (
				standard_chart_of_accounts_with_account_number,
			)

			return standard_chart_of_accounts_with_account_number.get()
		else:
			path = frappe.get_app_path("erpnext_france", "regional", "france", "chart_of_accounts")
			if not os.path.exists(path):
				pass

			for fname in os.listdir(path):
				fname = frappe.as_unicode(fname)
				if fname.endswith(".json"):
					with open(os.path.join(path, fname)) as f:
						chart = f.read()
						if chart and json.loads(chart).get("name") == chart_template:
							return json.loads(chart).get("tree")
	return chart
