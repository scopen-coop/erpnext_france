# Copyright (c) 2022, Dokos SAS and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.utils import cint
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def setup(company=None, patch=True):
	setup_company_independent_fixtures()
	if not patch:
		make_fixtures(company)
		set_accounting_journal_as_mandatory()


def setup_company_independent_fixtures():
	make_custom_fields()
	add_custom_roles_for_reports()


def make_custom_fields(update=True):
	invoice_item_fields = [
		dict(
			fieldname="tax_rate",
			label="Tax Rate",
			fieldtype="Float",
			insert_after="item_tax_template",
			print_hide=1,
			read_only=1,
		),
		dict(
			fieldname="tax_amount",
			label="Tax Amount",
			fieldtype="Currency",
			insert_after="tax_rate",
			print_hide=1,
			read_only=1,
			options="Company:company:default_currency",
		),
		dict(
			fieldname="total_amount",
			label="Total Amount",
			fieldtype="Currency",
			insert_after="tax_amount",
			print_hide=1,
			read_only=1,
			options="Company:company:default_currency",
		),
	]

	custom_fields = {
		"Company": [
			dict(
				fieldname="siren_number",
				label="SIREN Number",
				fieldtype="Data",
				insert_after="website",
				translatable=0,
			)
		],
		"Account": [
			dict(
				fieldname="negative_in_balance_sheet",
				label="Negative in Balance Sheet",
				fieldtype="Check",
				insert_after="include_in_gross",
				depends_on='eval:doc.report_type=="Balance Sheet" && !doc.is_group',
				description="Balance is debit for asset or credit for liability accounts",
				default=1,
			),
			dict(
				fieldname="balance_sheet_alternative_category",
				label="Balance Sheet Mirror Category",
				fieldtype="Link",
				options="Account",
				insert_after="negative_in_balance_sheet",
				depends_on='eval:doc.report_type=="Balance Sheet" && !doc.is_group && !doc.negative_in_balance_sheet',
				translatable=0,
			),
		],
		"Purchase Invoice Item": invoice_item_fields,
		"Sales Order Item": invoice_item_fields,
		"Delivery Note Item": invoice_item_fields,
		"Sales Invoice Item": invoice_item_fields,
		"Quotation Item": invoice_item_fields,
		"Purchase Order Item": invoice_item_fields,
		"Purchase Receipt Item": invoice_item_fields,
		"Supplier Quotation Item": invoice_item_fields,
		"Customer": [
			dict(fieldname="customer_info_section", fieldtype="Section Break", insert_after="image"),
			dict(
				fieldname="siren_number",
				label="SIREN Number",
				fieldtype="Data",
				insert_after="customer_info_section",
				translatable=0,
				allow_in_quick_entry=1,
			),
		],
		"Supplier": [
			dict(fieldname="supplier_info_section", fieldtype="Section Break", insert_after="image"),
			dict(
				fieldname="siren_number",
				label="SIREN Number",
				fieldtype="Data",
				insert_after="supplier_info_section",
				translatable=0,
				allow_in_quick_entry=1,
			),
		],
		"Address": [
			dict(
				fieldname="siret_number",
				label="SIRET Number",
				fieldtype="Data",
				insert_after="tax_category",
				translatable=0,
			),
		],
	}

	create_custom_fields(custom_fields, ignore_validate=frappe.flags.in_patch, update=update)


def add_custom_roles_for_reports():
	report_name = "Fichier des Ecritures Comptables [FEC]"

	if not frappe.db.get_value("Custom Role", dict(report=report_name)):
		frappe.get_doc(
			dict(doctype="Custom Role", report=report_name, roles=[dict(role="Accounts Manager")])
		).insert()


def make_fixtures(company=None):
	company = company if company else frappe.db.get_value("Global Defaults", None, "default_company")
	company_doc = frappe.get_doc("Company", company)

	if company_doc.chart_of_accounts == "Plan Comptable Général":
		accounts = frappe.get_all(
			"Account",
			filters={"disabled": 0, "is_group": 0, "company": company},
			fields=["name", "account_number"],
		)
		account_map = default_accounts_mapping(accounts, company_doc)
		for account in account_map:
			frappe.db.set_value("Company", company, account, account_map[account])


def default_accounts_mapping(accounts, company):
	account_map = {
		"inter_banks_transfer_account": 580,
		"default_receivable_account": 411,
		"round_off_account": 658,
		"write_off_account": 658,
		"discount_allowed_account": 709,
		"discount_received_account": 609,
		"exchange_gain_loss_account": 666,
		"unrealized_exchange_gain_loss_account": 686,
		"default_payable_account": 401,
		"default_expense_account": 600,
		"default_income_account": 706 if company.domain == "Services" else 701,
		"default_deferred_revenue_account": 487,
		"default_deferred_expense_account": 486,
		"default_inventory_account": 310,
		"stock_adjustment_account": 603,
		"stock_received_but_not_billed": 4081,
		"default_provisional_account": 4081,
		"accumulated_depreciation_account": 281,
		"depreciation_expense_account": 681,
		"disposal_account": 675,
		"capital_work_in_progress_account": 231,
		"asset_received_but_not_billed": 722,
		"default_advance_received_account": 4191,
		"default_advance_paid_account": 4091,
	}

	return {
		x: ([y.name for y in accounts if cint(y.account_number) == account_map[x]] or [""])[0]
		for x in account_map
	}


def set_accounting_journal_as_mandatory():
	frappe.db.set_single_value("Accounts Settings", "mandatory_accounting_journal", 1)
