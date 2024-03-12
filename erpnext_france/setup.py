# Copyright (c) 2022, Dokos SAS and Contributors
# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def setup_wizard_complete(args, action=None):
	add_bank_account(args)
	set_default_stock_settings()
	set_default_system_settings()
	set_default_print_settings()


def setup_migrate():
	set_default_stock_settings()
	set_default_system_settings()
	set_default_print_settings()

def setup_company_default(company, action):
	if company.country != 'France':
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
	company.db_set("payment_terms", 'Règlement à 30 jours')

	frappe.local.flags.ignore_chart_of_accounts = True


def default_accounts_mapping(accounts):
	account_map = {
		"default_bank_account": 5121,
		"default_cash_account": 5311,
		"default_receivable_account": 4111,
		"default_payable_account": 4011,
	}

	return {
		x: ([y.name for y in accounts if cint(y.account_number) == account_map[x]] or [""])[0]
		for x in account_map
	}


def add_bank_account(args):

	account = frappe.get_last_doc(
		"Account",
		filters={"disabled": 0, "is_group": 0, "company": args.get('company_name'), "account_number": 5121},
	)

	if not account:
		return

	frappe.db.set_value(
		"Company",
		args.get("company_name"),
		"default_bank_account",
		account.name,
		update_modified=False,
	)


def set_default_stock_settings():
	frappe.reload_doctype("Stock Settings")
	frappe.db.set_single_value("Stock Settings", "item_naming_by", "Item Code")
	frappe.db.set_default("item_naming_by", "Item Code")
	frappe.db.set_single_value("Stock Settings", "valuation_method", "Moving Average")
	frappe.db.set_single_value("Stock Settings", "stock_uom", "Unité")
	frappe.db.set_default("stock_uom", "Unité")
	frappe.db.set_single_value("Stock Settings", "auto_insert_price_list_rate_if_missing", 1)

def set_default_system_settings():
	frappe.db.set_single_value("System Settings", "first_day_of_the_week", "Monday")

def set_default_print_settings():
	frappe.reload_doctype("Print Settings")
	frappe.db.set_single_value("Print Settings", "print_style", "Modern")
	frappe.db.set_single_value("Print Settings", "with_letterhead", 1)
	frappe.db.set_single_value("Print Settings", "allow_page_break_inside_tables", 1)
