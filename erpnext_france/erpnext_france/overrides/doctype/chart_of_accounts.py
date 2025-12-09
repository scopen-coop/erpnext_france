# Copyright (c) 2024, Scopen.fr
# License: GNU General Public License v3. See license.txt

import json
import os

import frappe
from frappe import _
from frappe.utils import cstr
from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import (
	get_account_tree_from_existing_company,
	get_chart,
	get_charts_for_country,
	identify_is_group
)


@frappe.whitelist()
def get_charts_for_country_fr(country, with_standard=False):
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


def get_chart_fr(chart_template, existing_company=None):
	chart = {}
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

@frappe.whitelist()
def build_tree_from_json(chart_template, chart_data=None, from_coa_importer=False):

	"""get chart template from its folder and parse the json to be rendered as tree"""
	chart = chart_data or get_chart_fr(chart_template)

	# if no template selected, return as it is
	if not chart:
		return

	accounts = []

	def _import_accounts(children, parent):
		if isinstance(children, str):
			return
		"""recursively called to form a parent-child based list of dict from chart template"""
		for account_name, child in children.items():
			account = {}
			if account_name in [
				"account_name",
				"account_number",
				"account_type",
				"root_type",
				"is_group",
				"tax_rate",
				"account_currency",
			]:
				continue

			if from_coa_importer:
				account_name = child["account_name"]

			account["parent_account"] = parent
			if isinstance(child, str):
				account["expandable"] = False
				account["value"] = account_name
			else:
				account["expandable"] = True if identify_is_group(child) else False
				account["value"] = (
					(cstr(child.get("account_number")).strip() + " - " + account_name)
					if child.get("account_number")
					else account_name
				)
			accounts.append(account)
			_import_accounts(child, account["value"])

	_import_accounts(chart, None)
	return accounts



@frappe.whitelist()
def get_coa(doctype, parent, is_root=None, chart=None):
	# add chart to flags to retrieve when called from expand all function
	chart = chart if chart else frappe.flags.chart
	frappe.flags.chart = chart

	# CELA NE MARCHE PAS A CAUSE D'uUN BUG dans le standard ici la trad n'est pas prise en compte
	parent = None if parent in [_("All Accounts"), 'Tous les comptes'] else parent
	accounts = build_tree_from_json(chart)  # returns alist of dict in a tree render-able form

	# filter out to show data for the selected node only
	accounts = [d for d in accounts if d["parent_account"] == parent]

	return accounts
