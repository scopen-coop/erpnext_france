# -*- coding: utf-8 -*-
# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

app_name = "erpnext_france"
app_title = "ERPNext France"
app_publisher = "Scopen"
app_description = "App for french localization"
app_icon = "octicon octicon-home"
app_color = "#318CE7"
app_email = "contact@scopen.fr"
app_license = "GNU General Public License"

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [
			["name", "in", (
					"Accounts Settings-invoice_and_billing_tab",
					"Bank Account-swift_number",
					"Bank Transaction-category",
					"Bank Transaction-credit",
					"Bank Transaction-debit",
					"Company-accounting_export",
					"Company-export_file_format",
					"Company-siret",
					"Company-discount_supplier_account",
					"Customer-check_vat_id",
					"Customer-code_naf",
					"Customer-incoterm",
					"Customer-legal_form",
					"Customer-siret",
					"Customer-siren",
					"GL Entry-accounting_entry_number",
					"GL Entry-accounting_journal",
					"Item-down_payment_percentage",
					"Item-is_down_payment_item",
					"Mode of Payment Account-discount_supplier_account",
					"Mode of Payment Account-journal_label",
					"Party Account-advance_account",
					"Payment Entry-down_payment",
					"Payment Entry-accounting_journal",
					"Payment Entry-subscription",
					"Purchase Invoice-accounting_export_date",
					"Sales Invoice-accounting_export_date",
					"Sales Invoice-accounting_journal",
					"Sales Invoice-down_payment_section",
					"Sales Invoice-down_payment_against",
					"Sales Invoice-get_down_payment",
					"Sales Invoice-is_down_payment_invoice",
					"Sales Invoice-subscription",
					"Sales Invoice Advance-is_down_payment",
					"Sales Invoice Item-down_payment_rate",
					"Sales Invoice Item-is_down_payment_item",
					"Sales Invoice Item-tax_rate",
					"Sales Invoice Item-tax_amount",
					"Sales Invoice Item-total_amount",
					"Subscription-customer",
					"Subscription-total",
					"Subscription-recurrence_period",
					"Supplier-check_vat_id",
					"Supplier-code_naf",
					"Supplier-legal_form",
					"Supplier-siret",
					"Supplier-siren",
					"Party Account-subledger_account"
				)
			],
		]
	},
	{
		"dt": "Property Setter",
		"filters": [
			["name", "in",
			 (
				'Fiscal Year Company-read_only_onload',
				'Mode of Payment Account-read_only_onload',
				'Period Closing Voucher-main-autoname',
				'Period Closing Voucher-main-naming_rule',
				"Customer-tax_id-allow_in_quick_entry",
				"Sales Invoice-is_return-depends_on",
				"Sales Invoice Advance-allocated_amount-depends_on",
				"Sales Invoice Item-sales_order-read_only_depends_on",
				"Item-is_fixed_asset-depends_on",
				"Item-standard_rate-depends_on",
				"Item-include_item_in_manufacturing-depends_on",
				"Item-is_stock_item-depends_on",
				"Item-allow_alternative_item-depends_on",
			 	"Account-account_number-read_only"
			 )]
		]
	},
	{
		"dt": "Workspace",
		"filters": [
			["name", "in",
			 ('ERPNext France Settings',
			  'ERPNext France Export')]
		]
	},
	{
		"dt": "Workspace Link",
		"filters": [
			["label", "in",
			 ('ERPNext France',
			  'ERPNext France Settings',
			  'Legal Form',
			  'Company',
			  'Code Naf',
			  'Accounting Journal',
			  'Fichier des Ecritures Comptables [FEC]',
			  'Adjustement Entry',
			  'Export Comptable'
			  )],
		]
	},
	{
		"dt": "Address Template",
		"filters": [
			["country", "in", 'France']
		]
	},
	{
		"dt": "Legal Form",
	},
	{
		"dt": "Code Naf",
	},
	{
		"dt": "Report",
		"filters": [
			["name", "in", (
				'Fichier des Ecritures Comptables [FEC]',
				'General Ledger',
			)]
		]
	},
	{
		"dt": "Payment Terms Template",
		"filters": [
			["name", "in", 'Règlement à 30 jours']
		]
	},
	{
		"dt": "Payment Term",
		"filters": [
			["name", "in", 'Règlement à 30 jours']
		]
	},
	{
		"dt": "Print Format",
		"filters": [
			["name", "in", 'Devis-France']
		]
	}
]
# fixtures = ["Custom Field"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext_france/css/erpnext_france.css"
# app_include_js = "/assets/erpnext_france/js/erpnext_france.js"

# include js, css files in header of web template
# web_include_css = "/assets/erpnext_france/css/erpnext_france.css"
# web_include_js = "/assets/erpnext_france/js/erpnext_france.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doctype_js = {
	"Customer": ["public/js/customer.js", "public/js/party_check_vat.js"],
	"Supplier": ["public/js/supplier.js", "public/js/party_check_vat.js"],
	"Sales Order": ["public/js/sales_order.js"],
	"Purchase Invoice": ["public/js/purchase_invoice.js"],
	"Sales Invoice": ["public/js/sales_invoice.js"],
	"Company": ["public/js/company.js"],
}

doctype_list_js = {
	"Customer": ["public/js/fetch_from_sirene.js"],
	"Supplier": ["public/js/fetch_from_sirene.js"],
	"Payment Entry": ["public/js/payment_entry_list.js"],
}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "erpnext_france.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "erpnext_france.install.before_install"
# after_install = "erpnext_france.install.after_install"
after_install = "erpnext_france.install.after_install"
after_sync = "erpnext_france.utils.update_workspace.add_cards"
after_migrate = "erpnext_france.migrate.move_subledger_account_by_company"
setup_wizard_complete = "erpnext_france.setup.setup_wizard_complete"
# setup_wizard_complete = "erpnext_france.install.after_wizard"
# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpnext_france.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
	"Purchase Invoice": {
		"on_submit": "erpnext_france.erpnext_france.purchase_invoice.purchase_invoice.correct_gl_entry_supplier_discount"
	},
	"Sales Invoice": {
		"on_trash": "erpnext_france.utils.transaction_log.check_deletion_permission",
		"on_submit": [
			"erpnext_france.utils.transaction_log.create_transaction_log",
		],
	},
	"Payment Entry": {
		"on_trash": "erpnext_france.utils.transaction_log.check_deletion_permission",
		"on_submit": "erpnext_france.utils.transaction_log.create_transaction_log"
	},
	"GL Entry": {
		"on_submit": "erpnext_france.utils.accounting_entry_number.add_accounting_entry_number",
	},
	"Payment Ledger Entry": {
		"on_update": "erpnext_france.controllers.ple_down_payment.on_update"
	},
	"Journal Entry": {
		"validate": "erpnext_france.controllers.journal_entry_down_payment.validate"
	},
	"Company": {
		"after_insert": "erpnext_france.setup.setup_company_default"
	},
	"System Settings":{
		# "on_update": 'erpnext_france.install.after_wizard'
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"erpnext_france.tasks.all"
# 	],
# 	"daily": [
# 		"erpnext_france.tasks.daily"
# 	],
# 	"hourly": [
# 		"erpnext_france.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erpnext_france.tasks.weekly"
# 	]
# 	"monthly": [
# 		"erpnext_france.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "erpnext_france.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.stock.get_item_details.get_item_details": "erpnext_france.controllers.get_item_details_down_payment.get_item_details_down_payment"
}

# Regional Overrides
regional_overrides = {
	"France": {
		"erpnext.controllers.taxes_and_totals.update_itemised_tax_data": "erpnext_france.regional.france.taxes.update_itemised_tax_data",
		"erpnext.controllers.taxes_and_totals.get_itemised_tax": "erpnext_france.regional.france.taxes.get_itemised_tax",
		"erpnext.accounts.report.balance_sheet.balance_sheet.execute": "erpnext_france.regional.france.report.balance_sheet.balance_sheet.execute",
		"erpnext.accounts.controllers.accounts_controller.update_against_document_in_jv": "erpnext_france.controllers.accounts_controller.update_against_document_in_jv",
	},
}

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Payment Entry": "erpnext_france.erpnext_france.overrides.doctype.payment_entry_down_payment.PaymentEntryDownPayment",
	"Sales Invoice": "erpnext_france.erpnext_france.overrides.doctype.sales_invoice_down_payment.SalesInvoiceDownPayment",
}


export_python_type_annotations = True