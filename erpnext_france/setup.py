# Copyright (c) 2022, Dokos SAS and Contributors
# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint
from frappe.exceptions import DoesNotExistError
from frappe import _


def setup_wizard_complete(args, action=None):
    try:
        add_bank_account(args)
        set_4191_account_type(args)
        set_6241_account_type(args)
        set_4084_account_type(args)
        set_default_stock_settings()
        set_default_system_settings()
        set_default_print_settings()
    except E:
        frappe.throw('here' + str(E))
def setup_migrate():
    try:
        set_default_stock_settings()
        set_default_system_settings()
        set_default_print_settings()
        set_default_source_letter_head()
    except E:
        frappe.throw('here' + str(E))


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
    company.db_set("payment_terms", "Règlement à 30 jours")
    company.create_default_warehouses()
    set_default_accounting_journal(company.company_name, company.abbr)

    frappe.local.flags.ignore_chart_of_accounts = True


def default_accounts_mapping(accounts):
    account_map = {
        "default_cash_account": 5311,
        "default_receivable_account": 4111,
        "default_payable_account": 4011,
        "asset_received_but_not_billed": 4084,
        "default_expense_account": 6011,
        "default_income_account": 7011,
    }

    return {
        x: (
            [y.name for y in accounts if cint(y.account_number) == account_map[x]]
            or [""]
        )[0]
        for x in account_map
    }


def add_bank_account(args):
    try:
        account = frappe.get_last_doc(
            "Account",
            {
                "disabled": 0,
                "is_group": 0,
                "company": args.get("company_name"),
                "account_number": 5121,
            },
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

    except DoesNotExistError:
        frappe.msgprint(
            _(
                "ERPNext France - Company accounting auto setup cannot be done with chart of account without code"
            )
        )
        return


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
        if not account:
            return

        account.account_type = "Income Account"
        account.save()

    except DoesNotExistError:
        frappe.msgprint(
            _(
                "ERPNext France - Company accounting auto setup cannot be done with chart of account without code"
            )
        )
        return


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

        if not account:
            return

        account.account_type = "Chargeable"
        account.save()

    except DoesNotExistError:
        frappe.msgprint(
            _(
                "ERPNext France - Company accounting auto setup cannot be done with chart of account without code"
            )
        )
        return


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

        if not account:
            return

        account.account_type = "Asset Received But Not Billed"
        account.save()

    except DoesNotExistError:
        frappe.msgprint(
            _(
                "ERPNext France - Company accounting auto setup cannot be done with chart of account without code"
            )
        )
        return


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
    frappe.db.set_single_value(
        "Stock Settings", "auto_insert_price_list_rate_if_missing", 1
    )


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

    journal2 = frappe.get_doc(
        {
            "doctype": "Accounting Journal",
            "journal_code": "VT" + journal_code,
            "journal_name": "Vente",
            "type": "Sales",
            "company": company_name,
            "conditions": [{"document_type": "Sales Invoice"}],
        }
    )
    journal2.insert()

    journal3 = frappe.get_doc(
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
    journal3.insert()


def set_default_system_settings():
    try:
        frappe.reload_doctype("System Settings")
        frappe.db.set_single_value("System Settings", "first_day_of_the_week", "Monday")
        frappe.db.set_default("first_day_of_the_week", "Monday")
    except DoesNotExistError:
        frappe.msgprint(
            _(
                "ERPNext France - Error in System settings default"
            )
        )
        return

def set_default_print_settings():
    try :
        frappe.reload_doctype("Print Settings")
        frappe.db.set_single_value("Print Settings", "print_style", "Modern")
        frappe.db.set_single_value("Print Settings", "with_letterhead", 1)
        frappe.db.set_single_value("Print Settings", "allow_page_break_inside_tables", 1)
    except DoesNotExistError:
        frappe.msgprint(
            _(
                "ERPNext France - Error in print settings default"
            )
        )
        return