# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt


app_name = "erpnext_france"
app_title = "ERPNext France"
app_publisher = "Scopen"
app_description = "App for french localization"
app_icon = "octicon octicon-home"
app_color = "#318CE7"
app_email = "contact@scopen.fr"
app_license = "GNU General Public License"
source_link = "https://github.com/scopen-coop/erpnext_france"
fixtures = [
	{
		"dt": "Custom Field",
		"filters": [
			[
				"name",
				"in",
				(
					"Accounts Settings-invoice_and_billing_tab",
					"Bank Account-swift_number",
					"Bank Transaction-category",
					"Bank Transaction-credit",
					"Bank Transaction-debit",
					"Company-accounting_export",
					"Company-export_file_format",
					"Company-siret",
					"Company-discount_supplier_account",
					"Company-code_naf",
					"Company-legal_form",
					"Company-eori_number",
					"Company-capital",
					"Company-type_export_fec",
					"Company-column_break_898956",
					"Company-default_payment_terms_template_before_invoice",
					"Company-account_code_length",
					"Company-sepa_section",
					"Company-sepa_ics",
					"Customer-check_vat_id",
					"Customer-code_naf",
					"Customer-incoterm",
					"Customer-legal_form",
					"Customer-siret",
					"Customer-siren",
					"Customer-default_payment_terms_template_before_invoice",
					"Customer-sepa_section",
					"Customer-default_mode_of_payment_sepa",
					"Customer-column_break_sepa_1",
					"Customer-sepa_mandate",
					"Customer Group-default_payment_terms_template_before_invoice",
					"Customer Group-tax_category",
					"GL Entry-accounting_entry_number",
					"GL Entry-accounting_journal",
					"GL Entry-export_date",
					"Item-is_down_payment_item",
					"Item-eco_part",
					"Quotation-custom_do_not_calc_france_vat",
					"Mode of Payment Account-discount_supplier_account",
					"Mode of Payment Account-journal_label",
					"Party Account-advance_account",
					"Party Account-subledger_account",
					"Payment Entry-down_payment",
					"Payment Entry-accounting_journal",
					"Payment Entry-subscription",
					"Payment Term-payment_terms_before_invoice",
					"Payment Term-date_computed_based_on",
					"Payment Terms Template-template_payment_terms_before_invoice",
					"Payment Terms Template-payment_terms_before_invoice",
					"Purchase Order-custom_do_not_calc_france_vat",
					"Purchase Invoice-custom_do_not_calc_france_vat",
					"Purchase Invoice Item-supplier_part_no",
					"Purchase Invoice-accounting_export_date",
					"Purchase Taxes and Charges-ecotax",
					"Purchase Taxes and Charges-ecotax_tva_linked",
					"Sales Invoice-accounting_export_date",
					"Sales Invoice-accounting_journal",
					"Sales Invoice-down_payment_section",
					"Sales Invoice-down_payment_value",
					"Sales Invoice-down_payment_type",
					"Sales Invoice-down_payment_against",
					"Sales Invoice-get_down_payment",
					"Sales Invoice-is_down_payment_invoice",
					"Sales Invoice-subscription",
					"Sales Invoice-custom_do_not_calc_france_vat",
					"Sales Invoice Advance-is_down_payment",
					"Sales Invoice Item-down_payment_rate",
					"Sales Invoice Item-is_down_payment_item",
					"Sales Invoice Item-tax_rate",
					"Sales Invoice Item-tax_amount",
					"Sales Invoice Item-total_amount",
					"Sales Order-custom_do_not_calc_france_vat",
					"Sales Taxes and Charges-ecotax",
					"Sales Taxes and Charges-ecotax_tva_linked",
					"Subscription-customer",
					"Subscription-total",
					"Subscription-recurrence_period",
					"Supplier-check_vat_id",
					"Supplier-code_naf",
					"Supplier-legal_form",
					"Supplier-siret",
					"Supplier-siren",
					"Supplier Group-tax_category",
					"Purchase Invoice Item-supplier_part_no",
					"Quotation Item-is_presentation_line",
					"Quotation Item-display_type",
					"Quotation Item-section_label",
					"Quotation Item-subtotal_amount",
					"Sales Order Item-is_presentation_line",
					"Sales Order Item-display_type",
					"Sales Order Item-section_label",
					"Sales Order Item-subtotal_amount",
					"Sales Invoice Item-is_presentation_line",
					"Sales Invoice Item-display_type",
					"Sales Invoice Item-section_label",
					"Sales Invoice Item-subtotal_amount",
				),
			],
		],
	},
	{
		"dt": "Property Setter",
		"filters": [
			[
				"name",
				"in",
				(
					"Fiscal Year Company-read_only_onload",
					"Mode of Payment Account-read_only_onload",
					"Period Closing Voucher-main-autoname",
					"Period Closing Voucher-main-naming_rule",
					"Customer-tax_id-allow_in_quick_entry",
					"Customer-payment_terms-fetch_if_empty",
					"Customer-payment_terms-fetch_from",
					"Customer-tax_category-fetch_if_empty",
					"Customer-tax_category-fetch_from",
					"Sales Invoice-is_return-depends_on",
					"Sales Invoice-outstanding_amount-allow_on_submit",
					"Sales Invoice Advance-allocated_amount-depends_on",
					"Sales Invoice Item-sales_order-read_only_depends_on",
					"Item-is_fixed_asset-depends_on",
					"Item-standard_rate-depends_on",
					"Item-include_item_in_manufacturing-depends_on",
					"Item-is_stock_item-depends_on",
					"Item-allow_alternative_item-depends_on",
					"Address-main-field_order",
					"Opportunity-opportunity_type-translatable",
					"Opportunity-opportunity_type-default",
					"Opportunity Type-main-translated_doctype",
					"Item Price-brand-in_list_view",
					"Item Price-customer-in_list_view",
					"Item Price-item_code-in_list_view",
					"Item Price-item_name-in_list_view",
					"Item Price-price_list_rate-in_list_view",
					"Item Price-price_list-in_list_view",
					"Item Price-reference-in_list_view",
					"Item Price-supplier-in_list_view",
					"Item Price-uom-in_list_view",
					"Item Price-valid_from-in_list_view",
					"Item Price-valid_upto-in_list_view",
					"Item-grant_commission-default",
					"Payment Term-due_date_based_on-depends_on",
					"Payment Term-section_break_8-depends_on",
					"Payment Term-credit_days-depends_on",
					"Payment Term-credit_months-depends_on",
					"Payment Term-main-field_order",
					"Payment Terms Template-terms-depends_on",
					"Payment Terms Template-terms-mandatory_depends_on",
					"Payment Terms Template-terms-reqd",
					"Payment Terms Template Detail-payment_term-link_filters",
					"Payment Schedule-payment_term-allow_on_submit",
					"Payment Schedule-description-allow_on_submit",
					"Payment Schedule-due_date-allow_on_submit",
					"Payment Schedule-payment_amount-allow_on_submit",
					"Payment Schedule-invoice_portion-allow_on_submit",
					"Sales Order-payment_schedule-label",
					"Sales Order-payment_schedule-allow_on_submit",
					"Sales Order-payment_terms_template-label",
					"Sales Invoice-items-read_only_depends_on",
					"Sales Invoice-taxes-read_only_depends_on",
					"Quotation-payment_schedule-label",
					"Quotation-payment_terms_template-label",
					"Purchase Order Item-supplier_part_no-print_hide",
					"Purchase Order Item-supplier_part_no-hidden",
					"Purchase Order Item-supplier_part_no-read_only",
					"Request for Quotation Item-supplier_part_no-hidden",
					"Request for Quotation Item-supplier_part_no-read_only",
					"Stock Entry Type-main-translated_doctype",
					"Supplier-tax_category-fetch_if_empty",
					"Supplier-tax_category-fetch_from",
					"Supplier Quotation Item-supplier_part_no-print_hide",
					"Supplier Quotation Item-supplier_part_no-hidden",
					"Supplier Quotation Item-supplier_part_no-read_only",
					"Quotation Item-item_code-reqd",
					"Quotation Item-item_code-mandatory_depends_on",
					"Quotation Item-item_name-reqd",
					"Quotation Item-item_name-mandatory_depends_on",
					"Quotation Item-uom-reqd",
					"Quotation Item-uom-mandatory_depends_on",
					"Sales Order Item-item_code-reqd",
					"Sales Order Item-item_code-mandatory_depends_on",
					"Sales Order Item-item_name-reqd",
					"Sales Order Item-item_name-mandatory_depends_on",
					"Sales Order Item-uom-reqd",
					"Sales Order Item-uom-mandatory_depends_on",
					"Sales Invoice Item-item_code-reqd",
					"Sales Invoice Item-item_code-mandatory_depends_on",
					"Sales Invoice Item-item_name-reqd",
					"Sales Invoice Item-item_name-mandatory_depends_on",
					"Sales Invoice Item-uom-reqd",
					"Sales Invoice Item-uom-mandatory_depends_on",
				),
			]
		],
	},
	{"dt": "Address Template", "filters": [["country", "in", "France"]]},
	{
		"dt": "Legal Form",
	},
	{
		"dt": "Code Naf",
	},
	{
		"dt": "Report",
		"filters": [
			[
				"name",
				"in",
				(
					"Fichier des Ecritures Comptables [FEC]",
					"General Ledger",
				),
			]
		],
	},
	{"dt": "Letter Head", "filters": [["name", "in", "France Letter Head"]]},
	{
		"dt": "Print Format",
		"filters": [["name", "in", ("Sales Invoice with Presentation Lines",)]],
	},
	{"dt": "Variant Field", "filters": [["field_name", "in", "eco_part"]]},
	{"dt": "List View Settings", "filters": [["name", "=", "Item Price"]]},
	{
		"dt": "Bank Account Type",
		"filters": [
			[
				"name",
				"in",
				(
					"Caisse liquide",
					"Compte Courant",
					"Épargne",
				),
			]
		],
	},
]

# fixtures = ["Custom Field"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext_france/css/erpnext_france.css"
# app_include_js = "/assets/erpnext_france/js/erpnext_france.js"
app_include_js = [
	"erpnext_france.bundle.js",
]

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
	"Customer": ["public/js/party.js", "public/js/party_check_vat.js"],
	"Customer Group": ["public/js/customer_group.js"],
	"Supplier": ["public/js/party.js", "public/js/party_check_vat.js"],
	"Sales Order": ["public/js/sales_order.js", "public/js/presentation_lines.js"],
	"Purchase Invoice": ["public/js/purchase_invoice.js"],
	"Sales Invoice": ["public/js/sales_invoice.js", "public/js/presentation_lines.js"],
	"Quotation": ["public/js/quotation.js", "public/js/presentation_lines.js"],
	"Company": ["public/js/company.js"],
	"Item": ["public/js/item.js"],
	"Bank Transaction": ["public/js/bank_transaction.js"],
}

doctype_list_js = {
	"Customer": ["public/js/fetch_from_sirene.js"],
	"Supplier": ["public/js/fetch_from_sirene.js"],
	"Payment Entry": ["public/js/payment_entry_list.js"],
	"Item Price": ["public/js/item_price_list.js"],
	"Task": ["public/js/task_list.js"],
	"Sales Invoice": ["public/js/sales_invoice_list.js"],
	"Purchase Invoice": ["public/js/purchase_invoice_list.js"],
}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# "Role": "home_page"
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
after_sync = "erpnext_france.setup.make_payment_terms_fixtures"
setup_wizard_complete = "erpnext_france.setup.setup_wizard_complete"
after_migrate = [
	"erpnext_france.migrate.move_subledger_account_by_company",
	"erpnext_france.install.after_install",
	"erpnext_france.setup.setup_migrate",
	"erpnext_france.setup.make_payment_terms_fixtures",
	"erpnext_france.controllers.presentation_lines.setup_presentation_lines",
]

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
# }
# }
doc_events = {
	"Purchase Invoice": {
		"on_submit": "erpnext_france.erpnext_france.purchase_invoice.purchase_invoice.correct_gl_entry_supplier_discount",
		"before_save": [
			"erpnext_france.controllers.supplier_item_no.before_save",
			"erpnext_france.controllers.taxes.before_save",
		],
	},
	"Purchase Order": {
		"before_save": [
			"erpnext_france.controllers.supplier_item_no.before_save",
			"erpnext_france.controllers.taxes.before_save",
		]
	},
	"Supplier Quotation": {
		"before_save": "erpnext_france.controllers.supplier_item_no.before_save",
	},
	"Request for Quotation": {
		"before_save": "erpnext_france.controllers.supplier_item_no.before_save_request_for_quotation",
	},
	"Sales Invoice": {
		"on_trash": "erpnext_france.utils.transaction_log.check_deletion_permission",
		"on_submit": [
			"erpnext_france.utils.transaction_log.create_transaction_log",
		],
		"before_save": "erpnext_france.controllers.taxes.before_save",
		"before_validate": "erpnext_france.controllers.presentation_lines.before_validate",
		"validate": [
			"erpnext_france.erpnext_france.overrides.sales_invoice.validate",
			"erpnext_france.controllers.presentation_lines.validate",
		],
	},
	"Sales Order": {
		"before_update_after_submit": "erpnext_france.controllers.sales_order.verify_sales_orders_terms",
		"before_save": "erpnext_france.controllers.taxes.before_save",
		"before_validate": "erpnext_france.controllers.presentation_lines.before_validate",
		"validate": "erpnext_france.controllers.presentation_lines.validate",
	},
	"Payment Entry": {
		"on_trash": "erpnext_france.utils.transaction_log.check_deletion_permission",
		"on_submit": [
			"erpnext_france.utils.transaction_log.create_transaction_log",
			"erpnext_france.controllers.down_payment_invoice.set_paid_amount_of_linked_invoice",
		],
	},
	"GL Entry": {
		"on_submit": "erpnext_france.utils.accounting_entry_number.add_accounting_entry_number",
	},
	"Payment Ledger Entry": {"on_update": "erpnext_france.controllers.ple_down_payment.on_update"},
	"Journal Entry": {"validate": "erpnext_france.controllers.journal_entry_down_payment.validate"},
	"Company": {"after_insert": "erpnext_france.setup.setup_company_default"},
	"Item": {"on_update": "erpnext_france.controllers.item.on_update"},
	"Item Price": {"on_update": "erpnext_france.controllers.item_price.before_save"},
	"Quotation": {
		"before_save": "erpnext_france.controllers.taxes.before_save",
		"before_validate": "erpnext_france.controllers.presentation_lines.before_validate",
		"validate": "erpnext_france.controllers.presentation_lines.validate",
	},
	"System Settings": {
		# "on_update": 'erpnext_france.install.after_wizard'
	},
	"Bank Transaction": {
		"on_submit": "erpnext_france.regional.france.sepa_utils.auto_reconcile_sepa_transaction"
	},
	"SEPA Mandate": {
		"on_update": "erpnext_france.erpnext_france.doctype.sepa_mandate.sepa_mandate.sync_mandate_to_customer"
	},
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

scheduler_events = {
	"daily": ["erpnext_france.tasks.check_sirene_update"],
}

# Testing
# -------

# before_tests = "erpnext_france.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.controllers.accounts_controller.get_payment_term_details": "erpnext_france.controllers.party.get_payment_term_details",
	"erpnext.accounts.party.get_party_details": "erpnext_france.controllers.party.get_party_details",
	"erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice": "erpnext_france.controllers.sales_order.make_sales_invoice_with_payment_terms",
	"erpnext.selling.doctype.customer.customer.make_quotation": "erpnext_france.controllers.party.make_quotation_with_payment_terms",
}

# Regional Overrides
regional_overrides = {
	"France": {
		# "erpnext.controllers.taxes_and_totals.update_itemised_tax_data": "erpnext_france.controllers.taxes.update_itemised_tax_data",
		# "erpnext.controllers.taxes_and_totals.get_itemised_tax_breakup_data": "erpnext_france.controllers.taxes.get_itemised_tax_breakup_data",
		# "erpnext.controllers.taxes_and_totals.get_itemised_tax": "erpnext_france.regional.france.taxes.get_itemised_tax", #Not regionnalized
		# "erpnext.accounts.controllers.accounts_controller.update_against_document_in_jv": "erpnext_france.controllers.accounts_controller.update_against_document_in_jv", #Not regionnalized
	},
}

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Payment Entry": "erpnext_france.erpnext_france.overrides.doctype.payment_entry_down_payment.PaymentEntryDownPayment",
	"Sales Invoice": "erpnext_france.erpnext_france.overrides.doctype.sales_invoice_down_payment.SalesInvoiceDownPayment",
	"Payment Terms Template": "erpnext_france.erpnext_france.overrides.doctype.payment_terms_template.PaymentTermsTemplateWithTermsBeforeInvoice",
}

override_doctype_dashboards = {
	# "Payment Term": "erpnext_france.dashboard.payment_term.get_dashboard_data.get_dashboard_data",
}

export_python_type_annotations = True

jinja = {
	"methods": [
		"erpnext_france.utils.jinja_methods.build_ecopart_table",
		"erpnext_france.utils.jinja_methods.get_ecopart_table",
	],
}
