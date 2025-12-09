# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import erpnext
import frappe
from erpnext import get_company_currency
from erpnext.accounts.party import (
	get_due_date,
	get_party_advance_account,
	get_party_gle_account,
	get_party_gle_currency,
	set_address_details,
	set_contact_details,
	set_other_values,
	set_price_list,
	set_taxes,
)
from erpnext.selling.doctype.quotation.quotation import make_sales_order
from frappe import _, scrub
from frappe.utils import add_days, cint, flt, getdate, nowdate

from erpnext_france.controllers.accounts_controller import get_payment_term_details


@frappe.whitelist()
def get_party_account(party_type, party=None, company=None, include_advance=False, down_payment=None):
	"""Returns the account for the given `party`.
	Will first search in party (Customer / Supplier) record, if not found,
	will search in group (Customer Group / Supplier Group),
	finally will return default."""
	if not party_type:
		frappe.throw(_("Party Type is mandatory"))
	if not company:
		frappe.throw(_("Please select a Company"))

	if not party and party_type in ["Customer", "Supplier"]:
		default_account_name = (
			"default_receivable_account" if party_type == "Customer" else "default_payable_account"
		)

		return frappe.get_cached_value("Company", company, default_account_name)

	account = frappe.db.get_value(
		"Party Account", {"parenttype": party_type, "parent": party, "company": company}, "account"
	)

	if not account and party_type in ["Customer", "Supplier"]:
		party_group_doctype = "Customer Group" if party_type == "Customer" else "Supplier Group"
		group = frappe.get_cached_value(party_type, party, scrub(party_group_doctype))
		account = frappe.db.get_value(
			"Party Account",
			{"parenttype": party_group_doctype, "parent": group, "company": company},
			"account",
		)

	if not account and party_type in ["Customer", "Supplier"]:
		default_account_name = (
			"default_receivable_account" if party_type == "Customer" else "default_payable_account"
		)
		account = frappe.get_cached_value("Company", company, default_account_name)

	existing_gle_currency = get_party_gle_currency(party_type, party, company)
	if existing_gle_currency:
		if account:
			account_currency = frappe.get_cached_value("Account", account, "account_currency")
		if (account and account_currency != existing_gle_currency) or not account:
			account = get_party_gle_account(party_type, party, company)

	# get default account on the basis of party type
	if not account:
		account_type = frappe.get_cached_value("Party Type", party_type, "account_type")
		default_account_name = "default_" + account_type.lower() + "_account"
		account = frappe.get_cached_value("Company", company, default_account_name)

	# ERPNEXT FRANCE
	if (include_advance or cint(down_payment)) and party_type in ["Customer", "Supplier", "Student"]:
		# END ERPNEXT FRANCE
		advance_account = get_party_advance_account(party_type, party, company)
		if advance_account:
			return [account, advance_account]
		else:
			return [account]

	return account


@frappe.whitelist()
def get_party_details(
	party=None,
	account=None,
	party_type="Customer",
	company=None,
	posting_date=None,
	bill_date=None,
	price_list=None,
	currency=None,
	doctype=None,
	ignore_permissions=False,
	fetch_payment_terms_template=True,
	party_address=None,
	company_address=None,
	shipping_address=None,
	dispatch_address=None,
	pos_profile=None,
	down_payment=None,
):
	if not party:
		return {}
	if not frappe.db.exists(party_type, party):
		frappe.throw(_("{0}: {1} does not exists").format(party_type, party))
	return _get_party_details(
		party,
		account,
		party_type,
		company,
		posting_date,
		bill_date,
		price_list,
		currency,
		doctype,
		ignore_permissions,
		fetch_payment_terms_template,
		party_address,
		company_address,
		shipping_address,
		dispatch_address,
		pos_profile,
		down_payment,
	)


def _get_party_details(
	party=None,
	account=None,
	party_type="Customer",
	company=None,
	posting_date=None,
	bill_date=None,
	price_list=None,
	currency=None,
	doctype=None,
	ignore_permissions=False,
	fetch_payment_terms_template=True,
	party_address=None,
	company_address=None,
	shipping_address=None,
	dispatch_address=None,
	pos_profile=None,
	down_payment=None,
):
	# ERPNEXT FRANCE
	party_details = frappe._dict(
		set_account_and_due_date(
			party, account, party_type, company, posting_date, bill_date, doctype, down_payment
		)
	)
	# END ERPNEXT FRANCE
	party = party_details[party_type.lower()]
	party = frappe.get_doc(party_type, party)

	if not ignore_permissions:
		ptype = "select" if frappe.only_has_select_perm(party_type) else "read"
		frappe.has_permission(party_type, ptype, party, throw=True)

	currency = party.get("default_currency") or currency or get_company_currency(company)

	party_address, shipping_address = set_address_details(
		party_details,
		party,
		party_type,
		doctype,
		company,
		party_address,
		company_address,
		shipping_address,
		dispatch_address,
		ignore_permissions=ignore_permissions,
	)
	set_contact_details(party_details, party, party_type)
	set_other_values(party_details, party, party_type)
	set_price_list(party_details, party, party_type, price_list, pos_profile)

	tax_template = set_taxes(
		party.name,
		party_type,
		posting_date,
		company,
		customer_group=party_details.customer_group,
		supplier_group=party_details.supplier_group,
		tax_category=party_details.tax_category,
		billing_address=party_address,
		shipping_address=shipping_address,
	)

	if tax_template:
		party_details["taxes_and_charges"] = tax_template

	if cint(fetch_payment_terms_template):
		party_details["payment_terms_template"] = get_payment_terms_template(party.name, party_type, doctype, company)

	if not party_details.get("currency"):
		party_details["currency"] = currency

	# sales team
	if party_type == "Customer":
		party_details["sales_team"] = [
			{
				"sales_person": d.sales_person,
				"allocated_percentage": d.allocated_percentage or None,
				"commission_rate": d.commission_rate,
			}
			for d in party.get("sales_team")
		]

	# supplier tax withholding category
	if party_type == "Supplier" and party:
		party_details["supplier_tds"] = frappe.get_value(party_type, party.name, "tax_withholding_category")

	if not party_details.get("tax_category") and pos_profile:
		party_details["tax_category"] = frappe.get_value("POS Profile", pos_profile, "tax_category")

	return party_details


def set_account_and_due_date(
	party, account, party_type, company, posting_date, bill_date, doctype, down_payment
):
	if doctype not in ["POS Invoice", "Sales Invoice", "Purchase Invoice"]:
		# not an invoice
		return {party_type.lower(): party}

	if party:
		# ERPNEXT FRANCE
		account = get_party_account(party_type, party, company, down_payment)
		# END ERPNEXT FRANCE

	account_fieldname = "debit_to" if party_type == "Customer" else "credit_to"
	out = {
		party_type.lower(): party,
		account_fieldname: account,
		"due_date": get_due_date(posting_date, party_type, party, company, bill_date),
	}

	return out


def get_payment_terms_template(party_name, party_type, doctype, company=None):
	if party_type not in ("Customer", "Supplier"):
		return

	if party_type == "Customer":
		# ERPNEXT FRANCE
		if doctype in ("Quotation", "Sales Order"):
			payment_terms_template_field = "default_payment_terms_template_before_invoice"
		else:
			payment_terms_template_field = "payment_terms"
		customer = frappe.get_cached_value(
			"Customer", party_name, fieldname=[payment_terms_template_field, "customer_group"], as_dict=1
		)
		if doctype in ("Quotation", "Sales Order"):
			template = customer.default_payment_terms_template_before_invoice
		else:
			template = customer.payment_terms
		# END ERPNEXT FRANCE

		if not template and customer.customer_group:
			template = frappe.get_cached_value("Customer Group", customer.customer_group, "payment_terms")
	else:
		supplier = frappe.get_cached_value(
			"Supplier", party_name, fieldname=["payment_terms", "supplier_group"], as_dict=1
		)
		template = supplier.payment_terms
		if not template and supplier.supplier_group:
			template = frappe.get_cached_value("Supplier Group", supplier.supplier_group, "payment_terms")

	if not template and company:
		template = frappe.get_cached_value("Company", company, fieldname="payment_terms")

	return template


@frappe.whitelist()
def make_quotation_with_payment_terms(source_name, target_doc=None):
	from erpnext.selling.doctype.customer.customer import make_quotation

	target_doc = make_quotation(source_name, target_doc)
	customer = frappe.get_cached_doc("Customer", source_name)
	target_doc.payment_terms_template = customer.default_payment_terms_template_before_invoice

	payment_schedule = get_payment_terms_before_invoice(
		doctype=target_doc.doctype,
		posting_date=nowdate(),
		payment_terms_template=target_doc.payment_terms_template,
	)

	target_doc.set("payment_schedule", payment_schedule)
	return target_doc


@frappe.whitelist()
def get_payment_terms_before_invoice(
	doctype,
	grand_total=None,
	base_grand_total=None,
	posting_date=None,
	delivery_date=None,
	payment_terms_template=None,
):
	if doctype not in ("Quotation", "Sales Order"):
		return

	if not payment_terms_template:
		return

	terms_doc = frappe.get_doc("Payment Terms Template", payment_terms_template)
	schedule = []
	if terms_doc.get("payment_terms_before_invoice"):
		for d in terms_doc.get("payment_terms_before_invoice"):
			term_details = get_payment_term_details(
				d, posting_date, grand_total, base_grand_total, delivery_date
			)
			schedule.append(term_details)

	return schedule
