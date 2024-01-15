# Copyright (c) 2023, Scopen and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
import erpnext.accounts.report.general_ledger.general_ledger as gl

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
	select_fields = """, accounting_entry_number, debit, credit, debit_in_account_currency,
		credit_in_account_currency """

	if filters.get("show_remarks"):
		if remarks_length := frappe.db.get_single_value(
			"Accounts Settings", "general_ledger_remarks_length"
		):
			select_fields += f",substr(remarks, 1, {remarks_length}) as 'remarks'"
		else:
			select_fields += """,remarks"""

	order_by_statement = "order by posting_date, account, creation"

	if filters.get("include_dimensions"):
		order_by_statement = "order by posting_date, creation"

	if filters.get("group_by") == "Group by Voucher":
		order_by_statement = "order by posting_date, voucher_type, voucher_no"
	if filters.get("group_by") == "Group by Account":
		order_by_statement = "order by account, posting_date, creation"

	if filters.get("include_default_book_entries"):
		filters["company_fb"] = frappe.get_cached_value(
			"Company", filters.get("company"), "default_finance_book"
		)

	dimension_fields = ""
	if accounting_dimensions:
		dimension_fields = ", ".join(accounting_dimensions) + ","

	transaction_currency_fields = ""
	if filters.get("add_values_in_transaction_currency"):
		transaction_currency_fields = (
			"debit_in_transaction_currency, credit_in_transaction_currency, transaction_currency,"
		)

	gl_entries = frappe.db.sql(
		"""
		select
			name as gl_entry, posting_date, account, party_type, party,
			voucher_type, voucher_subtype, voucher_no, {dimension_fields}
			cost_center, project, {transaction_currency_fields}
			against_voucher_type, against_voucher, account_currency,
			against, is_opening, creation {select_fields}
		from `tabGL Entry`
		where company=%(company)s {conditions}
		{order_by_statement}
	""".format(
			dimension_fields=dimension_fields,
			transaction_currency_fields=transaction_currency_fields,
			select_fields=select_fields,
			conditions=gl.get_conditions(filters),
			order_by_statement=order_by_statement,
		),
		filters,
		as_dict=1,
	)

	if filters.get("presentation_currency"):
		return gl.convert_to_presentation_currency(gl_entries, currency_map)
	else:
		return gl_entries