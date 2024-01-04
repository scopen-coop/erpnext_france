import json

import frappe
from frappe.utils import flt


def update_itemised_tax_data(doc):
	if not doc.taxes:
		return

	itemised_tax = get_itemised_tax(doc.taxes, True)

	# Remove non tax fees
	tax_accounts = set(
		itemised_tax[item][tax].get("tax_account") for item in itemised_tax for tax in itemised_tax[item]
	)
	tax_accounts = frappe.get_all(
		"Account",
		filters={"name": ("in", list(tax_accounts)), "account_type": "Tax"},
		fields=["name", "account_number"],
	)
	valid_tax_accounts = [t.name for t in tax_accounts]
	account_numbers = {t.name: t.accounr_number for t in tax_accounts}

	valid_itemised_tax = {}
	for item in itemised_tax:
		valid_itemised_tax[item] = {}
		for tax in itemised_tax[item]:
			if itemised_tax[item][tax].get("tax_account") in valid_tax_accounts:
				valid_itemised_tax[item][tax] = itemised_tax[item][tax]

	for row in doc.items:
		if not row.item_code:
			continue

		tax_rate = 0.0
		item_tax_rate = {}
		item_specific_rates = []

		if row.item_tax_rate:
			item_tax_rate = frappe.parse_json(row.item_tax_rate)

		# First check if tax rate is present
		# If not then look up in item_wise_tax_detail
		if item_tax_rate:
			for tax,tax_rate_detail in item_tax_rate.items():
				tax_rate += tax_rate_detail

		elif row.item_code and valid_itemised_tax.get(row.item_code):
			item_specific_rates = [
				tax
				for tax in valid_itemised_tax.get(row.item_code).items()
				if flt(tax[1].get("form_rate", 0)) != 0.0
			]

			tax_rate = sum(
				[
					tax.get("tax_rate", 0) * (-1 if tax.get("add_deduct_tax") == "Deduct" else 1)
					for d, tax in (item_specific_rates or valid_itemised_tax.get(row.item_code, {}).items())
				]
			)

		meta = frappe.get_meta(row.doctype)
		if meta.has_field("tax_rate"):
			row.tax_rate = flt(tax_rate, row.precision("tax_rate"))
			row.tax_amount = flt((row.base_net_amount * tax_rate) / 100, row.precision("base_net_amount"))
			row.total_amount = flt((row.base_net_amount + row.tax_amount), row.precision("total_amount"))

		row.item_tax_rate = json.dumps(
			[
				{
					"account": tax.get("tax_account"),
					"account_number": account_numbers.get(tax.get("tax_account")),
					"rate": tax.get("tax_rate", 0),
					"taxable_amount": row.get("base_net_amount"),
					"tax_amount": row.get("tax_amount"),
				}
				for d, tax in (item_specific_rates or valid_itemised_tax.get(row.item_code, {}).items())
			]
		)


def get_itemised_tax(taxes, with_tax_account=False):
	itemised_tax = {}
	for tax in taxes:
		if getattr(tax, "category", None) and tax.category == "Valuation":
			continue

		item_tax_map = json.loads(tax.item_wise_tax_detail) if tax.item_wise_tax_detail else {}
		if item_tax_map:
			for item_code, tax_data in item_tax_map.items():
				itemised_tax.setdefault(item_code, frappe._dict())

				tax_rate = 0.0
				tax_amount = 0.0

				if isinstance(tax_data, list):
					tax_rate = flt(tax_data[0])
					tax_amount = flt(tax_data[1])
				else:
					tax_rate = flt(tax_data)

				if not tax_rate and tax_amount:
					tax_rate = flt(frappe.db.get_value("Account", tax.account_head, "tax_rate"))

				itemised_tax[item_code][tax.description] = frappe._dict(
					dict(
						tax_rate=tax_rate,
						tax_amount=tax_amount,
						add_deduct_tax=tax.get("add_deduct_tax"),
						form_rate=tax.rate,
					)
				)

				if with_tax_account:
					itemised_tax[item_code][tax.description].tax_account = tax.account_head

	return itemised_tax
