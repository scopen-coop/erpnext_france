import json

import frappe
from erpnext.controllers.taxes_and_totals import get_itemised_taxable_amount
from erpnext.stock.get_item_details import get_conversion_factor
from frappe import _
from frappe.utils import flt, parse_json, round_based_on_smallest_currency_fraction


def before_save(doc, method):
	# Verif before update
	update_ecopart_taxes_for_item(doc)


def update_ecopart_taxes_for_item(doc):
	is_sales_doc = False
	if doc.doctype in ("Quotation", "Sales Invoice", "Sales Order"):
		is_sales_doc = True

	if len(doc.items) == 0:
		return

	(
		taxes_map,
		item_wise_tax_detail_before_tva,
		item_wise_tax_detail_with_tva,
		item_wise_tax_detail_standard_tva,
		used_ecopart_accounts,
		used_vat_accounts,
	) = create_ecopart_taxes_map(doc, is_sales_doc)

	# Remove all Taxes
	delete_taxes(doc)

	for vat_account in used_vat_accounts:
		if vat_account:
			create_update_ecopart_with_vat_taxes(
				doc,
				taxes_map,
				item_wise_tax_detail_before_tva,
				item_wise_tax_detail_with_tva,
				used_ecopart_accounts,
				vat_account,
				is_sales_doc,
			)
			create_update_vat_taxes(doc, item_wise_tax_detail_standard_tva, vat_account, is_sales_doc)
		else:
			create_update_ecopart_without_vat_taxes(
				doc, item_wise_tax_detail_before_tva, taxes_map, used_ecopart_accounts, is_sales_doc
			)

	for vat_account in used_vat_accounts:
		if vat_account:
			create_update_autoliquidation_taxes(
				doc, item_wise_tax_detail_standard_tva, vat_account, is_sales_doc
			)

	reorder_tax(doc)

	taxes_rate = [tax.rate for tax in doc.taxes]

	from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals

	calculate_taxes_and_totals(doc)

	# Because tax.rate is set to None in tax and totals if tax.charge_type is Actual
	for i, tax in enumerate(doc.taxes):
		tax.rate = taxes_rate[i]


def reorder_tax(doc):
	# Étape 1 : Séparer les taxes selon leur type
	regular_taxes = [tax for tax in doc.taxes if tax.charge_type == "Actual" and not tax.ecotax]
	ecopart_taxes = [tax for tax in doc.taxes if tax.charge_type == "Actual" and tax.ecotax]
	dependent_taxes = [tax for tax in doc.taxes if tax.charge_type not in ["Actual"]]

	# Étape 2 : Réorganiser les taxes dans le bon ordre
	reordered_taxes = regular_taxes + ecopart_taxes + dependent_taxes
	# Étape 3 : Mémoriser les anciens idx avant modification
	old_idx_map = {id(tax): tax.idx for tax in reordered_taxes}

	# Étape 4 : Réassigner les nouveaux idx et créer le mapping ancien_idx -> nouveau_idx
	old_to_new_idx = {}
	for new_idx, tax in enumerate(reordered_taxes, start=1):
		old_idx = old_idx_map[id(tax)]
		old_to_new_idx[old_idx] = new_idx
		tax.idx = new_idx

	# Étape 5 : Mettre à jour les row_id pour les taxes dépendantes
	for tax in reordered_taxes:
		if hasattr(tax, "row_id") and tax.row_id in old_to_new_idx:
			tax.row_id = old_to_new_idx[tax.row_id]

	# Étape 6 : Réassigner la liste finale à doc.taxes
	doc.taxes = reordered_taxes


def create_update_ecopart_without_vat_taxes(
	doc, item_wise_tax_detail_before_tva, taxes_map, used_ecopart_accounts, is_sales_doc
):
	for ecopart_account in used_ecopart_accounts:
		if ecopart_account not in item_wise_tax_detail_before_tva[None]:
			continue

		item_tax_wise = item_wise_tax_detail_before_tva[None][ecopart_account]
		item_code_2_keep = []
		for item_code in item_tax_wise:
			if item_code in item_wise_tax_detail_before_tva[None][ecopart_account].keys():
				item_code_2_keep.append(item_code)

		item_tax_wise = {item_code: [0, item_tax_wise[item_code]] for item_code in item_code_2_keep}
		if taxes_map is not None and None in taxes_map:
			total_tax = taxes_map[None][ecopart_account]
			create_update_ecotax(doc, None, ecopart_account, None, item_tax_wise, total_tax, is_sales_doc)


def create_ecopart_taxes_map(doc, is_sales_doc):
	used_ecopart_accounts = []
	used_vat_accounts = []
	item_map = {}
	taxes_map = {}
	taxes_itemised_map = {}

	for doc_item in doc.items:
		item = frappe.get_doc("Item", doc_item.item_code)

		vat_accounts = init_taxes_map_and_vat_account(doc, doc_item, item, taxes_map, is_sales_doc)
		if len(vat_accounts) > 0:
			for vat_account in vat_accounts:
				if vat_account not in used_vat_accounts:
					used_vat_accounts.append(vat_account)

				if len(item.eco_part):
					create_item_and_tax_maps_with_ecopart(
						doc_item,
						item,
						taxes_itemised_map,
						taxes_map,
						vat_account,
						used_ecopart_accounts,
						is_sales_doc,
					)
				create_item_and_tax_maps_without_ecopart(
					doc_item,
					item_map,
					vat_account,
				)
		elif len(item.eco_part):
			if None not in used_vat_accounts:
				used_vat_accounts.append(None)

			create_item_and_tax_maps_with_ecopart(
				doc_item, item, taxes_itemised_map, taxes_map, None, used_ecopart_accounts, is_sales_doc
			)

	(
		item_wise_tax_detail_before_tva,
		item_wise_tax_detail_standard_tva,
		item_wise_tax_detail_with_tva,
	) = build_item_wise_taxes_map(
		item_map, taxes_itemised_map, taxes_map, used_ecopart_accounts, used_vat_accounts
	)

	return (
		taxes_map,
		item_wise_tax_detail_before_tva,
		item_wise_tax_detail_with_tva,
		item_wise_tax_detail_standard_tva,
		used_ecopart_accounts,
		used_vat_accounts,
	)


def init_taxes_map_and_vat_account(doc, doc_item, item, taxes_map, is_sales_doc):
	vat_accounts = []
	if doc_item.item_tax_template:
		item_tax_template = frappe.get_doc("Item Tax Template", doc_item.item_tax_template)
		for tax in item_tax_template.taxes:
			if tax.tax_type not in taxes_map:
				taxes_map[tax.tax_type] = {}
			vat_accounts.append(tax.tax_type)
	elif doc.taxes_and_charges:
		if is_sales_doc:
			taxes_and_charges_template = frappe.get_doc(
				"Sales Taxes and Charges Template", doc.taxes_and_charges
			)
		else:
			taxes_and_charges_template = frappe.get_doc(
				"Purchase Taxes and Charges Template", doc.taxes_and_charges
			)
		for tax in taxes_and_charges_template.taxes:
			if tax.account_head not in taxes_map:
				taxes_map[tax.account_head] = {}
			vat_accounts.append(tax.account_head)
	elif len(item.taxes) > 0:
		item_tax_template = frappe.get_doc("Item Tax Template", item.taxes[0].get("item_tax_template"))

		for tax in item_tax_template.taxes:
			if tax.tax_type not in taxes_map:
				taxes_map[tax.tax_type] = {}
			vat_accounts.append(tax.tax_type)
	return vat_accounts


def create_item_and_tax_maps_with_ecopart(
	doc_item, item, taxes_itemised_map, taxes_map, vat_account, used_ecopart_accounts, is_sales_doc
):
	for ecopart in item.eco_part:
		if vat_account not in taxes_map:
			taxes_map[vat_account] = {}

		ecopart_account = ecopart.sell_account if is_sales_doc else ecopart.buy_account

		if ecopart_account not in taxes_map[vat_account]:
			taxes_map[vat_account][ecopart_account] = 0

		if vat_account not in taxes_itemised_map:
			taxes_itemised_map[vat_account] = {}

		if ecopart_account not in taxes_itemised_map[vat_account]:
			taxes_itemised_map[vat_account][ecopart_account] = {}

		if doc_item.item_code not in taxes_itemised_map[vat_account][ecopart_account]:
			taxes_itemised_map[vat_account][ecopart_account][doc_item.item_code] = 0

		conversion_factor_obj = get_conversion_factor(doc_item.item_code, doc_item.uom)
		conversion_factor = conversion_factor_obj.get("conversion_factor") if not None else 1

		taxes_map[vat_account][ecopart_account] += ecopart.amount * doc_item.qty / conversion_factor
		taxes_itemised_map[vat_account][ecopart_account][doc_item.item_code] += (
			ecopart.amount * doc_item.qty / conversion_factor
		)

		if ecopart_account not in used_ecopart_accounts:
			used_ecopart_accounts.append(ecopart_account)


def create_item_and_tax_maps_without_ecopart(
	doc_item,
	item_map,
	vat_account,
):
	if vat_account not in item_map:
		item_map[vat_account] = {}

	if doc_item.item_code not in item_map[vat_account]:
		item_map[vat_account][doc_item.item_code] = 0

	item_map[vat_account][doc_item.item_code] += doc_item.amount


def build_item_wise_taxes_map(
	item_map, taxes_itemised_map, taxes_map, used_ecopart_accounts, used_vat_accounts
):
	item_wise_tax_detail_standard_tva = {}
	item_wise_tax_detail_before_tva = {}
	item_wise_tax_detail_with_tva = {}
	for vat_account in used_vat_accounts:
		if vat_account not in taxes_map:
			continue

		if vat_account not in item_wise_tax_detail_with_tva:
			item_wise_tax_detail_with_tva[vat_account] = {}
			item_wise_tax_detail_standard_tva[vat_account] = {}

		tax_rate = frappe.get_value("Account", vat_account, "tax_rate") or 0

		for ecopart_account in used_ecopart_accounts:
			if ecopart_account not in taxes_map[vat_account]:
				continue

			tax_itemised = taxes_itemised_map[vat_account][ecopart_account]

			if ecopart_account not in item_wise_tax_detail_with_tva[vat_account]:
				item_wise_tax_detail_with_tva[vat_account][ecopart_account] = {}

			if vat_account not in item_wise_tax_detail_before_tva:
				item_wise_tax_detail_before_tva[vat_account] = {}

			if ecopart_account not in item_wise_tax_detail_before_tva[vat_account]:
				item_wise_tax_detail_before_tva[vat_account][ecopart_account] = {}

			for item_key in tax_itemised.keys():
				item_wise_tax_detail_before_tva[vat_account][ecopart_account][item_key] = tax_itemised[
					item_key
				]
				item_wise_tax_detail_with_tva[vat_account][ecopart_account][item_key] = [
					tax_rate,
					tax_itemised[item_key] * tax_rate / 100,
				]
		if vat_account in item_map:
			for item_key in item_map[vat_account].keys():
				item_wise_tax_detail_standard_tva[vat_account][item_key] = [
					tax_rate,
					item_map[vat_account][item_key] * tax_rate / 100,
				]

	return item_wise_tax_detail_before_tva, item_wise_tax_detail_standard_tva, item_wise_tax_detail_with_tva


def create_update_ecopart_with_vat_taxes(
	doc,
	taxes_map,
	item_wise_tax_detail_before_tva,
	item_wise_tax_detail_with_tva,
	used_ecopart_accounts,
	vat_account,
	is_sales_doc,
):
	for ecopart_account in used_ecopart_accounts:
		if not ecopart_account:
			continue

		if ecopart_account not in taxes_map[vat_account]:
			continue

		total_tax = taxes_map[vat_account][ecopart_account]

		# Check if tax already exists
		ecopart_tax = None
		ecopart_vat_tax = None

		for tax in doc.taxes:
			if tax.ecotax and tax.description == ecopart_account + "\n" + str(vat_account):
				ecopart_tax = tax
			elif (
				tax.charge_type == "On Previous Row Amount"
				and tax.account_head == vat_account
				and tax.description
				== _("Eco Part VAT: {0}").format(str(ecopart_account) + "\n" + str(vat_account))
			):
				ecopart_vat_tax = tax

		if (
			vat_account in item_wise_tax_detail_before_tva
			and ecopart_account in item_wise_tax_detail_before_tva[vat_account]
			and ecopart_account in item_wise_tax_detail_with_tva[vat_account]
		):
			item_tax_wise = item_wise_tax_detail_before_tva[vat_account][ecopart_account]
			item_code_2_keep = []
			for item_code in item_tax_wise:
				if item_code in item_wise_tax_detail_with_tva[vat_account][ecopart_account].keys():
					item_code_2_keep.append(item_code)

			item_tax_wise = {item_code: [0, item_tax_wise[item_code]] for item_code in item_code_2_keep}
			ecopart_tax = create_update_ecotax(
				doc, vat_account, ecopart_account, ecopart_tax, item_tax_wise, total_tax, is_sales_doc
			)

		# Need to be done outside the for loop to get ecopart_tax.idx
		if (
			vat_account in item_wise_tax_detail_with_tva
			and ecopart_account in item_wise_tax_detail_with_tva[vat_account]
		):
			item_tax_wise = item_wise_tax_detail_with_tva[vat_account][ecopart_account]
			create_update_vat_on_ecotax(
				doc,
				ecopart_tax.idx,
				ecopart_account,
				ecopart_vat_tax,
				total_tax,
				item_tax_wise,
				vat_account,
				is_sales_doc,
			)


def create_update_vat_taxes(doc, item_wise_tax_detail_standard_tva, vat_account, is_sales_doc):
	vat_tax = None
	for tax in doc.taxes:
		if (
			tax.charge_type == "Actual"
			and tax.account_head == vat_account
			and not tax.ecotax
			and vat_account in item_wise_tax_detail_standard_tva
		):
			vat_tax = tax

	item_tax_wise = item_wise_tax_detail_standard_tva[vat_account]
	taxe_description = get_taxe_description(vat_account)

	tax_amount = 0
	tax_rate = 0
	# Update with new values
	for item_code_vat_rate_amount in item_tax_wise.items():
		vat_rate_amount = item_code_vat_rate_amount[1]
		tax_rate = vat_rate_amount[0]
		tax_amount += vat_rate_amount[1]

	if vat_tax:
		vat_tax.tax_amount = tax_amount
		vat_tax.item_wise_tax_detail = json.dumps(item_tax_wise)
		vat_tax.dont_recompute_tax = True
	else:
		company = frappe.get_cached_doc("Company", doc.company)
		vat_tax = frappe.get_doc(
			{
				"doctype": "Sales Taxes and Charges" if is_sales_doc else "Purchase Taxes and Charges",
				"charge_type": "Actual",
				"cost_center": company.cost_center,
				"description": taxe_description,
				"account_head": vat_account,
				"parent": doc.name,
				"parenttype": doc.doctype,
				"tax_amount": tax_amount,
				"rate": tax_rate,
				"item_wise_tax_detail": json.dumps(item_tax_wise),
				"dont_recompute_tax": True,
			}
		)
		if not is_sales_doc:
			vat_tax.add_deduct_tax = "Add"
			vat_tax.category = "Total"

		doc.append("taxes", vat_tax)


def create_update_autoliquidation_taxes(doc, item_wise_tax_detail_standard_tva, vat_account, is_sales_doc):
	vat_tax = None
	corresponding_vat_tax = None
	ecotax_tax = None
	corresponding_ecotax_tax = None
	for tax in doc.taxes:
		if (
			tax.charge_type == "On Previous Row Amount"
			and tax.account_head == vat_account
			and not tax.ecotax
			and vat_account in item_wise_tax_detail_standard_tva
			and tax.rate < 0
		):
			vat_tax = tax

	if not vat_tax:
		return

	for tax in doc.taxes:
		if tax.charge_type == "On Previous Row Amount" and not tax.ecotax and tax.rate == vat_tax.rate * -1:
			corresponding_vat_tax = tax

	# Remove the taxe actual and change
	for tax in doc.taxes:
		if (
			tax.charge_type == "Actual"
			and tax.ecotax
			and vat_tax.account_head in json.loads(tax.ecotax_tva_linked)
		):
			ecotax_tax = tax

	if not corresponding_vat_tax:
		return

	for tax in doc.taxes:
		if (
			tax.charge_type == "Actual"
			and tax.ecotax
			and corresponding_vat_tax.account_head in json.loads(tax.ecotax_tva_linked)
		):
			corresponding_ecotax_tax = tax

	if not corresponding_ecotax_tax:
		return

	vat_tax.row_id = corresponding_ecotax_tax.idx

	existing_ecotax_tva_account = (
		json.loads(corresponding_ecotax_tax.ecotax_tva_linked)
		if corresponding_ecotax_tax.ecotax_tva_linked
		else []
	)
	if vat_tax.account_head not in existing_ecotax_tva_account:
		existing_ecotax_tva_account.append(vat_tax.account_head)

	corresponding_ecotax_tax.ecotax_tva_linked = json.dumps(existing_ecotax_tva_account)
	doc.taxes.remove(ecotax_tax)


def create_update_ecotax(
	doc, vat_account, ecopart_account, ecopart_tax, item_tax_wise, total_tax, is_sales_doc
):
	# Update existing tax rows if found
	if ecopart_tax:
		# Load existing item_wise_tax_detail
		existing_tax_detail = (
			json.loads(ecopart_tax.item_wise_tax_detail) if ecopart_tax.item_wise_tax_detail else {}
		)

		# Update with new values
		for key, value in item_tax_wise.items():
			if key in existing_tax_detail:
				existing_tax_detail[key] += value[1] if value is list else value
			else:
				existing_tax_detail[key] = value[1] if value is list else value

		existing_ecotax_tva_account = (
			json.loads(ecopart_tax.ecotax_tva_linked) if ecopart_tax.ecotax_tva_linked else []
		)
		if vat_account and vat_account not in existing_ecotax_tva_account:
			existing_ecotax_tva_account.append(vat_account)

		ecopart_tax.ecotax_tva_linked = json.dumps(existing_ecotax_tva_account)
		ecopart_tax.tax_amount += total_tax
		ecopart_tax.item_wise_tax_detail = json.dumps(existing_tax_detail)
		ecopart_tax.dont_recompute_tax = True
	else:
		company = frappe.get_cached_doc("Company", doc.company)

		taxe_description = get_taxe_description(ecopart_account)

		ecopart_tax = frappe.get_doc(
			{
				"doctype": "Sales Taxes and Charges" if is_sales_doc else "Purchase Taxes and Charges",
				"charge_type": "Actual",
				"cost_center": company.cost_center,
				"ecotax": True,
				"description": taxe_description,
				"account_head": ecopart_account,
				"tax_amount": total_tax,
				"tax_rate": 0,
				"parent": doc.name,
				"parenttype": doc.doctype,
				"ecotax_tva_linked": json.dumps([vat_account] if vat_account else []),
				"item_wise_tax_detail": json.dumps(item_tax_wise),
				"dont_recompute_tax": True,
			}
		)
		if not is_sales_doc:
			ecopart_tax.add_deduct_tax = "Add"
			ecopart_tax.category = "Total"
		doc.append("taxes", ecopart_tax)
	return ecopart_tax


def create_update_vat_on_ecotax(
	doc,
	ecopart_tax_idx,
	ecopart_account,
	ecopart_vat_tax,
	total_tax,
	item_tax_wise,
	vat_account,
	is_sales_doc,
):
	tax_rate = frappe.get_value("Account", vat_account, "tax_rate") or 0
	item_tax_wise = {item_code: item_tax_wise[item_code] for item_code in item_tax_wise}
	if ecopart_vat_tax:
		# Load existing item_wise_tax_detail
		existing_tax_detail = (
			json.loads(ecopart_vat_tax.item_wise_tax_detail) if ecopart_vat_tax.item_wise_tax_detail else {}
		)
		# Update with new values
		for key, value in item_tax_wise.items():
			if key in existing_tax_detail:
				existing_tax_detail[key] += value[0] or 0
			else:
				existing_tax_detail[key] = value[0] or 0

		ecopart_vat_tax.tax_amount = total_tax * tax_rate / 100
		ecopart_vat_tax.item_wise_tax_detail = json.dumps(existing_tax_detail)
		ecopart_vat_tax.row_id = ecopart_tax_idx
	else:
		vat_description = ""
		if vat_account:
			vat_description = get_taxe_description(vat_account)
		taxe_description = vat_description

		company = frappe.get_cached_doc("Company", doc.company)
		ecopart_vat_tax = frappe.get_doc(
			{
				"doctype": "Sales Taxes and Charges" if is_sales_doc else "Purchase Taxes and Charges",
				"charge_type": "On Previous Row Amount",
				"cost_center": company.cost_center,
				"description": _("Eco Part VAT: {0}").format(taxe_description),
				"account_head": vat_account,
				"tax_amount": 0,
				"row_id": ecopart_tax_idx,
				"rate": tax_rate,
				"item_wise_tax_detail": json.dumps(item_tax_wise),
				"dont_recompute_tax": True,
				"parent": doc.name,
				"parenttype": doc.doctype,
			}
		)

		if not is_sales_doc:
			ecopart_vat_tax.add_deduct_tax = "Add"
			ecopart_vat_tax.category = "Total"
		doc.append("taxes", ecopart_vat_tax)


def delete_taxes(doc):
	to_remove = []
	for taxe in doc.taxes:
		to_remove.append(taxe)

	# Ensure the removal actually happens
	for taxe in to_remove:
		doc.taxes.remove(taxe)

	if not doc.is_new():
		doc.db_update()


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
		if item_tax_rate and hasattr(item_tax_rate, "items"):
			for tax_tax_rate_detail in item_tax_rate.items():
				tax_rate_detail = tax_tax_rate_detail[1]
				tax_rate += tax_rate_detail if tax_rate_detail else 0

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


def get_itemised_tax_breakup_data(doc):
	itemised_tax = get_itemised_tax(doc.taxes)

	itemised_taxable_amount = get_itemised_taxable_amount(doc.items)
	itemised_tax_data = []
	for item_code, taxes in itemised_tax.items():
		itemised_tax_data.append(
			frappe._dict(
				{"item": item_code, "taxable_amount": itemised_taxable_amount.get(item_code, 0), **taxes}
			)
		)

	return itemised_tax_data


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

				if not tax.ecotax:
					tax_amount = tax_rate
					tax_rate = 0.0

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


def get_taxe_description(account):
	account = frappe.get_cached_doc("Account", account)
	taxe_description = str(account)
	if account.get("pdf_description"):
		taxe_description = account.get("pdf_description")
	return taxe_description
