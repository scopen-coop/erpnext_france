# Copyright (c) 2022, Dokos SAS and Contributors
# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt
import json
import os

import frappe
from frappe import _
from frappe.desk.page.setup_wizard.setup_wizard import make_records
from frappe.exceptions import DoesNotExistError
from frappe.utils import cint


def make_payment_terms_fixtures():
	base_path = frappe.get_app_path("erpnext_france", "data")
	payment_term_fixtures = os.path.join(base_path, "payment_term.json")
	payment_terms_template_fixtures = os.path.join(base_path, "payment_terms_template.json")

	with open(payment_term_fixtures) as json_file:
		docs = json.load(json_file)
		make_records(docs)

	with open(payment_terms_template_fixtures) as json_file:
		docs = json.load(json_file)
		make_records(docs)


def setup_wizard_complete(args, action=None):
	add_bank_account(args)
	set_4191_account_type(args)
	set_6241_account_type(args)
	set_4084_account_type(args)
	set_default_stock_settings()
	set_default_system_settings()
	set_default_print_settings()


def setup_migrate():
	set_default_stock_settings()
	set_default_system_settings()
	set_default_print_settings()
	set_default_source_letter_head()


def setup_company_default(company, action):
	if company.country != "France":
		return

	if not frappe.db.sql(
		"""select name from tabAccount
            where company=%s and docstatus<2 limit 1""",
		company.company_name,
	):
		company.name = company.company_name
		company.create_default_accounts()

	accounts = frappe.db.get_all(
		"Account",
		filters={"disabled": 0, "is_group": 0, "company": company.name},
		fields=["name", "account_number"],
	)

	account_map = default_accounts_mapping(accounts)
	for account in account_map:
		company.db_set(account, account_map[account])

	company.db_set("enable_perpetual_inventory", 0)
	company.db_set("payment_terms", "30 jours")
	company.db_set("default_payment_terms_template_before_invoice", "30% à la commande, 70% avant expédition")
	company.create_default_warehouses()
	set_default_accounting_journal(company.company_name, company.abbr)

	frappe.local.flags.ignore_chart_of_accounts = True


def default_accounts_mapping(accounts):
	account_map = {
		"default_cash_account": 53,
		"default_receivable_account": 4111,
		"default_payable_account": 4011,
		"asset_received_but_not_billed": 4084,
		"default_expense_account": 607,
		"default_income_account": 707,
	}

	return {
		x: ([y.name for y in accounts if cint(y.account_number) == account_map[x]] or [""])[0]
		for x in account_map
	}


def add_bank_account(args):
	try:
		account = frappe.get_last_doc(
			"Account",
			filters={
				"disabled": 0,
				"is_group": 0,
				"company": args.get("company_name"),
				"account_number": 5121,
			},
		)
	except DoesNotExistError:
		frappe.msgprint(
			_(
				"ERPNext France - Company accounting auto setup cannot be done with chart of account without code"
			)
		)
		return

	if not account:
		return

	frappe.db.set_value(
		"Company",
		args.get("company_name"),
		"default_bank_account",
		account.name,
		update_modified=False,
	)


def set_4191_account_type(args):
	try:
		account = frappe.get_last_doc(
			"Account",
			filters={
				"disabled": 0,
				"is_group": 0,
				"company": args.get("company_name"),
				"account_number": 4191,
			},
		)
	except DoesNotExistError:
		frappe.msgprint(
			_(
				"ERPNext France - Company accounting auto setup cannot be done with chart of account without code"
			)
		)
		return

	if not account:
		return

	account.account_type = "Payable"
	account.save()


def set_6241_account_type(args):
	try:
		account = frappe.get_last_doc(
			"Account",
			filters={
				"disabled": 0,
				"is_group": 0,
				"company": args.get("company_name"),
				"account_number": 6241,
			},
		)
	except DoesNotExistError:
		frappe.msgprint(
			_(
				"ERPNext France - Company accounting auto setup cannot be done with chart of account without code"
			)
		)
		return

	if not account:
		return

	account.account_type = "Chargeable"
	account.save()


def set_4084_account_type(args):
	try:
		account = frappe.get_last_doc(
			"Account",
			filters={
				"disabled": 0,
				"is_group": 0,
				"company": args.get("company_name"),
				"account_number": 4084,
			},
		)
	except DoesNotExistError:
		frappe.msgprint(
			_(
				"ERPNext France - Company accounting auto setup cannot be done with chart of account without code"
			)
		)
		return

	if not account:
		return

	account.account_type = "Asset Received But Not Billed"
	account.save()


def set_default_source_letter_head():
	letter_head = frappe.get_last_doc(
		"Letter Head",
		filters={"name": "France Letter Head"},
	)

	if not letter_head:
		return

	letter_head.source = "HTML"
	letter_head.save()


def set_default_stock_settings():
	frappe.reload_doctype("Stock Settings")
	frappe.db.set_single_value("Stock Settings", "item_naming_by", "Item Code")
	frappe.db.set_default("item_naming_by", "Item Code")
	frappe.db.set_single_value("Stock Settings", "valuation_method", "Moving Average")
	frappe.db.set_single_value("Stock Settings", "stock_uom", "Unité")
	frappe.db.set_default("stock_uom", "Unité")
	frappe.db.set_single_value("Stock Settings", "auto_insert_price_list_rate_if_missing", 1)


def set_default_accounting_journal(company_name, company_abbr):
	journal_code = ""
	if " (Demo)" in company_name:
		journal_code = " - Demo"
	elif company_abbr != "":
		journal_code = company_abbr

	journal = frappe.get_doc(
		{
			"doctype": "Accounting Journal",
			"journal_code": "AC" + journal_code,
			"journal_name": "Achat",
			"type": "Purchase",
			"company": company_name,
			"conditions": [{"document_type": "Purchase Invoice"}],
		}
	)
	journal.insert()

	journal = frappe.get_doc(
		{
			"doctype": "Accounting Journal",
			"journal_code": "VT" + journal_code,
			"journal_name": "Vente",
			"type": "Sales",
			"company": company_name,
			"conditions": [{"document_type": "Sales Invoice"}],
		}
	)
	journal.insert()

	journal = frappe.get_doc(
		{
			"doctype": "Accounting Journal",
			"journal_code": "BQ" + journal_code,
			"journal_name": "Banque",
			"type": "Bank",
			"company": company_name,
			"conditions": [
				{"document_type": "Payment Entry"},
				{"document_type": "Journal Entry"},
			],
		}
	)
	journal.insert()


def set_default_system_settings():
	frappe.db.set_single_value("System Settings", "first_day_of_the_week", "Monday")
	frappe.db.set_default("first_day_of_the_week", "Monday")


def set_default_print_settings():
	frappe.reload_doctype("Print Settings")
	frappe.db.set_single_value("Print Settings", "print_style", "Modern")
	frappe.db.set_single_value("Print Settings", "with_letterhead", 1)
	frappe.db.set_single_value("Print Settings", "allow_page_break_inside_tables", 1)
