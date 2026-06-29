# Copyright (c) 2021, scopen.fr and contributors
# For license information, please see license.txt

import json

import frappe
from erpnext.stock.get_item_details import (
	get_item_details,
	purchase_doctypes,
	sales_doctypes,
)
from frappe import _, get_hooks


@frappe.whitelist()
def get_item_details_account_code(args, doc=None, for_validate=False, overwrite_warehouse=True):
	# Chaînage avec d'éventuels autres hooks override_whitelisted_methods sur get_item_details
	hooks = get_hooks("override_whitelisted_methods", {}).get(
		"erpnext.stock.get_item_details.get_item_details", []
	)
	if hooks:
		current_method = __name__ + "." + get_item_details_account_code.__name__
		if current_method in hooks:
			current_hook_pos = hooks.index(current_method)
			if current_hook_pos > 0:
				method = frappe.get_attr(hooks[current_hook_pos - 1])
				out = method(args, doc, for_validate, overwrite_warehouse)
			else:
				out = get_item_details(args, doc, for_validate, overwrite_warehouse)
		else:
			out = get_item_details(args, doc, for_validate, overwrite_warehouse)
	else:
		out = get_item_details(args, doc, for_validate, overwrite_warehouse)

	# Normalisation de args (process_args supprimé en v16 — remplacé par normalize_ctx_input)
	if isinstance(args, str):
		args = frappe.parse_json(args)
	if not isinstance(args, frappe._dict):
		args = frappe._dict(args)

	if isinstance(doc, str):
		doc = json.loads(doc)

	# Déterminer le type de transaction et le tiers
	transaction_type = None
	type_thirdparty = None
	if doc:
		if doc.get("doctype") in purchase_doctypes:
			transaction_type = "Achat"
			type_thirdparty = "Supplier"
		if doc.get("doctype") in sales_doctypes:
			transaction_type = "Vente"
			type_thirdparty = "Customer"

	third_party = None
	if args.customer is not None:
		third_party = args.customer
	if args.supplier is not None:
		third_party = args.supplier

	# Sur Quotation il n'y a pas de code comptable
	if doc and doc.get("doctype") == "Quotation":
		type_thirdparty = None

	if type_thirdparty is not None and third_party is not None:
		account = get_correct_default_account(third_party, type_thirdparty, args.item_code)
		if transaction_type == "Vente" and account is not None:
			out.income_account = account
		if transaction_type == "Achat" and account is not None:
			out.expense_account = account

	return out


def get_correct_default_account(third_party, type_thirdparty, item_code):
	if third_party is None:
		return None

	doc_thirdparty = frappe.get_doc(type_thirdparty, third_party)
	categ_compta_thirdparty = doc_thirdparty.get("categorie_comptable_tiers")

	doc_item = frappe.get_doc("Item", item_code)
	account = None

	# Paramétrage global (singleton Special Item Accountancy Code Default)
	for thirdparty_setup_categ in frappe.db.get_all(
		doctype="Categorie Comptable Tiers Et Code Comptable Produit",
		as_list=True,
		filters={"parent": "Special Item Accountancy Code Default"},
	):
		thirdparty_categ = frappe.get_doc(
			"Categorie Comptable Tiers Et Code Comptable Produit",
			thirdparty_setup_categ[0],
		)
		if thirdparty_categ.get("categorie_comptable_tiers") == categ_compta_thirdparty:
			if type_thirdparty == "Customer":
				account = thirdparty_categ.get("compte_de_produits")
			if type_thirdparty == "Supplier":
				account = thirdparty_categ.get("compte_de_charges")
				break

	# Paramétrage par Item Group
	for item_group_categ in frappe.db.get_all(
		doctype="Categorie Comptable Tiers Et Code Comptable Produit",
		as_list=True,
		filters={"parent": doc_item.get("item_group"), "parenttype": "Item Group"},
	):
		thirdparty_categ = frappe.get_doc(
			"Categorie Comptable Tiers Et Code Comptable Produit",
			item_group_categ[0],
		)
		if thirdparty_categ.get("categorie_comptable_tiers") == categ_compta_thirdparty:
			if type_thirdparty == "Customer":
				account = thirdparty_categ.get("compte_de_produits")
			if type_thirdparty == "Supplier":
				account = thirdparty_categ.get("compte_de_charges")
				break

	# Paramétrage spécifique à l'article (priorité max)
	if doc_item.get("special_item_accountancy_code_details"):
		for detail in doc_item.get("special_item_accountancy_code_details"):
			if detail.categorie_comptable_tiers == categ_compta_thirdparty:
				if type_thirdparty == "Customer":
					account = detail.compte_de_produits
				if type_thirdparty == "Supplier":
					account = detail.compte_de_charges
				break

	return account


@frappe.whitelist()
def get_correct_default_account_validate(doc, method):
	if not doc:
		return

	if doc.get("doctype") in purchase_doctypes:
		supplier = frappe.get_doc("Supplier", doc.supplier)
		if not supplier.get("categorie_comptable_tiers"):
			frappe.throw(_("Customer accountancy category is missing"))
		for itm in doc.items:
			account = get_correct_default_account(doc.supplier, "Supplier", itm.item_code)
			if account:
				itm.expense_account = account

	if doc.get("doctype") in sales_doctypes:
		customer = frappe.get_doc("Customer", doc.customer)
		if not customer.get("categorie_comptable_tiers"):
			frappe.throw(_("Customer accountancy category is missing"))
		for itm in doc.items:
			account = get_correct_default_account(doc.customer, "Customer", itm.item_code)
			if account:
				itm.income_account = account
