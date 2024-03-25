# Copyright (c) 2023, Scopen and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
import erpnext.accounts.report.general_ledger.general_ledger as gl
from erpnext.accounts.report.general_ledger.general_ledger import (
	get_accounts_with_children, get_cost_centers_with_children, get_dimension_with_children
)


def execute(filters=None):
	if not filters:
		return [], []

	account_details = {}

	if filters and filters.get("print_in_account_currency") and not filters.get("account"):
		frappe.throw(_("Select an account to print in account currency"))

	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	if filters.get("party"):
		filters.party = frappe.parse_json(filters.get("party"))

	gl.validate_filters(filters, account_details)

	gl.validate_party(filters)

	filters = gl.set_account_currency(filters)

	columns = get_columns(filters)

	gl.update_translations()

	res = get_result(filters, account_details)

	return columns, res


def get_columns(filters):
	columns = gl.get_columns(filters)
	acc_journal_columns = {
		'label': _('Accounting Entry Number'),
		'fieldname': 'accounting_entry_number',
		'fieldtype': 'Link',
		'options': 'Accounting Journal'
	}

	columns.insert(0, acc_journal_columns)

	return columns


def get_result(filters, account_details):
	accounting_dimensions = []
	if filters.get("include_dimensions"):
		accounting_dimensions = gl.get_accounting_dimensions()

	gl_entries = get_gl_entries(filters, accounting_dimensions)

	data = gl.get_data_with_opening_closing(filters, account_details, accounting_dimensions, gl_entries)

	result = gl.get_result_as_list(data, filters)
	return result


def get_gl_entries(filters, accounting_dimensions):
	currency_map = gl.get_currency(filters)

	gle = frappe.qb.DocType("GL Entry")
	gl_entries = (
		frappe.qb.from_(gle)
		.select(
			gle.name.as_('gl_entry'),
			gle.posting_date,
			gle.account,
			gle.party_type,
			gle.party,
			gle.voucher_type,
			gle.voucher_subtype,
			gle.voucher_no,
			gle.cost_center,
			gle.project,
			gle.against_voucher_type,
			gle.against_voucher,
			gle.account_currency,
			gle.against,
			gle.is_opening,
			gle.creation,
			gle.accounting_entry_number,
			gle.debit,
			gle.credit,
			gle.debit_in_account_currency,
			gle.credit_in_account_currency
		)
	)
	# {dimension_fields}

	if filters.get("add_values_in_transaction_currency"):
		gl_entries = (
			gl_entries.select(
				gle.debit_in_transaction_currency,
				gle.credit_in_transaction_currency,
				gle.transaction_currency
			)
		)

	if accounting_dimensions:
		for dimension in accounting_dimensions:
			gl_entries = (
				gl_entries.select(
					gle[dimension]
				)
			)

	if filters.get("show_remarks"):
		gl_entries = (gl_entries.select(gle.remarks))

	order_by_statement = gl_entries.orderby(
		gle.posting_date,
		gle.account,
		gle.creation
	)

	if filters.get("include_dimensions"):
		order_by_statement = gl_entries.orderby(
			gle.posting_date,
			gle.creation
		)

	if filters.get("group_by") == "Group by Voucher":
		order_by_statement = gl_entries.orderby(
			gle.posting_date,
			gle.voucher_type,
			gle.voucher_no
		)
	if filters.get("group_by") == "Group by Account":
		order_by_statement = gl_entries.orderby(
			gle.account,
			gle.posting_date,
			gle.creation
		)

	gl_entries = order_by_statement

	if filters.get("include_default_book_entries"):
		filters["company_fb"] = frappe.get_cached_value(
			"Company", filters.get("company"), "default_finance_book"
		)

	gl_entries = get_conditions(filters, gle, gl_entries)

	if filters.get("presentation_currency"):
		return gl.convert_to_presentation_currency(gl_entries.run(as_dict=1), currency_map)
	else:
		return gl_entries.run(as_dict=1)


def get_conditions(filters, gle, gl_entries):
	filters_query = gl_entries
	if filters.get("account"):
		filters.account = get_accounts_with_children(filters.account)
		filters_query = (filters_query.where(gle.account.isin(filters.account)))

	if filters.get("cost_center"):
		filters.cost_center = get_cost_centers_with_children(filters.cost_center)
		filters_query = (filters_query.where(gle.cost_center.isin(filters.cost_center)))

	if filters.get("voucher_no"):
		filters_query = (filters_query.where(gle.voucher_no == filters.voucher_no))

	if filters.get("against_voucher_no"):
		filters_query = (filters_query.where(gle.against_voucher_no == filters.against_voucher_no))

	if filters.get("ignore_err"):
		err_journals = frappe.db.get_all(
			"Journal Entry",
			filters={
				"company": filters.get("company"),
				"docstatus": 1,
				"voucher_type": ("in", ["Exchange Rate Revaluation", "Exchange Gain Or Loss"]),
			},
			as_list=True,
		)
		if err_journals:
			filters.update({"voucher_no_not_in": [x[0] for x in err_journals]})

	if filters.get("voucher_no_not_in"):
		filters_query = (filters_query.where(gle.voucher_no.notin(filters.voucher_no_not_in)))

	if filters.get("group_by") == "Group by Party" and not filters.get("party_type"):
		filters_query = (filters_query.where(gle.party_type.isin('Customer', 'Supplier')))

	if filters.get("party_type"):
		filters_query = (filters_query.where(gle.party_type == filters.party_type))

	if filters.get("party"):
		filters_query = (filters_query.where(gle.party.isin(filters.party)))

	if not (
			filters.get("account")
			or filters.get("party")
			or filters.get("group_by") in ["Group by Account", "Group by Party"]
	):
		filters_query = (filters_query.where((gle.posting_date >= filters.from_date) | (gle.is_opening == 'Yes')))

	filters_query = (filters_query.where((gle.posting_date <= filters.to_date) | (gle.is_opening == 'Yes')))

	if filters.get("project"):
		filters_query = (filters_query.where(gle.project.isin(filters.project)))

	if filters.get("include_default_book_entries"):
		if filters.get("finance_book"):
			if filters.get("company_fb") and cstr(filters.get("finance_book")) != cstr(
					filters.get("company_fb")
			):
				frappe.throw(_("To use a different finance book, please uncheck 'Include Default FB Entries'"))
			else:
				filters_query = (
					filters_query.where((gle.finance_book.isin(filters.finance_book)) | (gle.finance_book.isnull())))
		else:
			filters_query = (
				filters_query.where((gle.finance_book.isin(('', filters.company_fb))) | (gle.finance_book.isnull())))
	else:
		if filters.get("finance_book"):
			filters_query = (
				filters_query.where((gle.finance_book.isin(filters.finance_book)) | (gle.finance_book.isnull())))
		else:
			filters_query = (filters_query.where((gle.finance_book.isin('')) | (gle.finance_book.isnull())))

	if not filters.get("show_cancelled_entries"):
		filters_query = (filters_query.where(gle.is_cancelled == 0))

	# from frappe.desk.reportview import build_match_conditions
	#
	# match_conditions = build_match_conditions("GL Entry")
	#
	# if match_conditions:
	# 	conditions.append(match_conditions)

	# accounting_dimensions = gl.get_accounting_dimensions(as_list=False)
	#
	# if accounting_dimensions:
	# 	for dimension in accounting_dimensions:
	# 		# Ignore 'Finance Book' set up as dimension in below logic, as it is already handled in above section
	# 		if not dimension.disabled and dimension.document_type != "Finance Book":
	# 			if filters.get(dimension.fieldname):
	# 				if frappe.get_cached_value("DocType", dimension.document_type, "is_tree"):
	# 					filters[dimension.fieldname] = get_dimension_with_children(
	# 						dimension.document_type, filters.get(dimension.fieldname)
	# 					)
	# 					conditions.append("{0} in %({0})s".format(dimension.fieldname))
	# 				else:
	# 					conditions.append("{0} in %({0})s".format(dimension.fieldname))

	return filters_query
