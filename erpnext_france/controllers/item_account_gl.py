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

# from erpnext.stock.get_item_details import process_string_args, validate_item_details


@frappe.whitelist()
def get_item_details_account_code(args, doc=None, for_validate=False, overwrite_warehouse=True):
	# find if other apps declare these override_whitelisted_methods
	# then get results from other hooks with this one
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
				# standard feature
				out = get_item_details(args, doc, for_validate, overwrite_warehouse)
		else:
			# standard feature
			out = get_item_details(args, doc, for_validate, overwrite_warehouse)
	else:
		# standard feature
		out = get_item_details(args, doc, for_validate, overwrite_warehouse)

	# ERPNEXT FRANCE: after standard execution

	# return out
	# Process arges and doc to use it as object
	args = frappe._dict(args)
	if isinstance(doc, str):
		doc = json.loads(doc)
	else:
		doc = args

	# deal with tax code selling or buying
	transaction_type = None
	type_thirdparty = None
	if doc:
		if doc.get("doctype") in purchase_doctypes:
			transaction_type = "Achat"
			type_thirdparty = "Supplier"
		if doc.get("doctype") in sales_doctypes:
			transaction_type = "Vente"
			type_thirdparty = "Customer"

	# by defaut we don't know what we are working on
	third_party = None
	if args.customer is not None:
		third_party = args.customer

	if args.supplier is not None:
		third_party = args.supplier

	# on Quotation there is no accountancy code
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
	if third_party is not None:
		doc_thirdparty = frappe.get_doc(type_thirdparty, third_party)
		categ_compta_thirdparty = doc_thirdparty.get("categorie_comptable_tiers")
		doc_item = frappe.get_doc("Item", item_code)
		account = None

		for thirdparty_setup_categ in frappe.db.get_all(
			doctype="Categorie comptable Tiers et code comptable Produit",
			as_list=True,
			filters={"parent": "Special Item Accountancy Code Default"},
		):
			thirdparty_categ = frappe.get_doc(
				"Categorie comptable Tiers et code comptable Produit",
				thirdparty_setup_categ[0],
			)
			if thirdparty_categ.get("categorie_comptable_tiers") == categ_compta_thirdparty:
				if type_thirdparty == "Customer":
					account = thirdparty_categ.get("compte_de_produits")
				if type_thirdparty == "Supplier":
					account = thirdparty_categ.get("compte_de_charges")
					break

		for item_group_categ in frappe.db.get_all(
			doctype="Categorie comptable Tiers et code comptable Produit",
			as_list=True,
			filters={"parent": doc_item.get("item_group"), "parenttype": "Item Group"},
		):
			thirdparty_categ = frappe.get_doc(
				"Categorie comptable Tiers et code comptable Produit",
				item_group_categ[0],
			)
			if thirdparty_categ.get("categorie_comptable_tiers") == categ_compta_thirdparty:
				if type_thirdparty == "Customer":
					account = thirdparty_categ.get("compte_de_produits")
				if type_thirdparty == "Supplier":
					account = thirdparty_categ.get("compte_de_charges")
					break

		if doc_item.get("special_item_accountancy_code_details") != 0:
			for detail in doc_item.get("special_item_accountancy_code_details"):
				if detail.categorie_comptable_tiers == categ_compta_thirdparty:
					if type_thirdparty == "Customer":
						account = detail.compte_de_produits
					if type_thirdparty == "Supplier":
						account = detail.compte_de_charges
					break

		return account

	return None


@frappe.whitelist()
def get_correct_default_account_validate(doc, method):
	if not doc:
		return
	if doc.get("doctype") in purchase_doctypes:
		change_account_on_item_based_on_thirdparty_accounting_category('supplier', doc)
	elif doc.get("doctype") in sales_doctypes:
		change_account_on_item_based_on_thirdparty_accounting_category('customer', doc)


def change_account_on_item_based_on_thirdparty_accounting_category(thirdparty_type, doc):
	account_type = 'income_account' if thirdparty_type == 'customer' else 'expense_account'

	thirdparty = frappe.get_doc(thirdparty_type.capitalize(), doc.get(thirdparty_type))
	if (thirdparty.get("categorie_comptable_tiers") is None) or (thirdparty.get("categorie_comptable_tiers") == ""):
		frappe.throw(_("Thirdparty accountancy category is missing"))

	for itm in doc.items:
		account = get_correct_default_account(doc.get(thirdparty_type), thirdparty_type.capitalize(), itm.item_code)
		origin_account = itm.get(account_type)
		if not account or account == origin_account:
			continue

		itm.set(account_type, account)
		frappe.msgprint(
			_("{0} on item {1} has been modified according to the thirdparty's accounting category from {2} to {3}").format(
				_(account_type), itm.item_code, origin_account, account
			))
