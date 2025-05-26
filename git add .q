[1mdiff --git a/erpnext_france/controllers/taxes.py b/erpnext_france/controllers/taxes.py[m
[1mindex 5b59dfa..5db61fd 100644[m
[1m--- a/erpnext_france/controllers/taxes.py[m
[1m+++ b/erpnext_france/controllers/taxes.py[m
[36m@@ -1,8 +1,8 @@[m
[32m+[m[32mimport json[m
 import frappe[m
 from frappe import _[m
[32m+[m[32mfrom frappe.utils import parse_json, flt, round_based_on_smallest_currency_fraction[m
 from erpnext.stock.get_item_details import get_uom_conv_factor[m
[31m-from frappe.utils import parse_json, flt[m
[31m-import json[m
 from erpnext.controllers.taxes_and_totals import get_itemised_taxable_amount[m
 [m
 def before_save(doc, method):[m
[36m@@ -55,12 +55,11 @@[m [mdef update_ecopart_taxes_for_item(doc):[m
 [m
 def reorder_tax(doc):[m
 	# Étape 1 : Séparer les taxes selon leur type[m
[31m-	regular_taxes = [tax for tax in doc.taxes if tax.charge_type == "On Net Total"][m
[31m-	ecopart_taxes = [tax for tax in doc.taxes if tax.charge_type == "Actual"][m
[31m-	dependent_taxes = [tax for tax in doc.taxes if tax.charge_type not in ["On Net Total", "Actual"]][m
[32m+[m	[32mregular_taxes = [tax for tax in doc.taxes if tax.charge_type == "Actual"][m
[32m+[m	[32mdependent_taxes = [tax for tax in doc.taxes if tax.charge_type not in ["Actual"]][m
 [m
 	# Étape 2 : Réorganiser les taxes dans le bon ordre[m
[31m-	reordered_taxes = regular_taxes + ecopart_taxes + dependent_taxes[m
[32m+[m	[32mreordered_taxes = regular_taxes + dependent_taxes[m
 [m
 	# Étape 3 : Mémoriser les anciens idx avant modification[m
 	old_idx_map = {id(tax): tax.idx for tax in reordered_taxes}[m
[36m@@ -83,11 +82,11 @@[m [mdef reorder_tax(doc):[m
 [m
 def create_update_ecopart_without_vat_taxes(doc, item_wise_tax_detail_before_tva, taxes_map, used_ecopart_accounts):[m
 	for ecopart_account in used_ecopart_accounts:[m
[31m-		if ecopart_account in item_wise_tax_detail_before_tva:[m
[31m-			item_tax_wise = item_wise_tax_detail_before_tva[ecopart_account][m
[32m+[m		[32mif ecopart_account in item_wise_tax_detail_before_tva[None]:[m
[32m+[m			[32mitem_tax_wise = item_wise_tax_detail_before_tva[None][ecopart_account][m
 			if taxes_map is not None and None in taxes_map:[m
 				total_tax = taxes_map[None][ecopart_account][m
[31m-				create_update_ecotax(doc, ecopart_account, None, item_tax_wise, total_tax)[m
[32m+[m				[32mcreate_update_ecotax(doc, None, ecopart_account, None, item_tax_wise, total_tax)[m
 [m
 [m
 def create_ecopart_taxes_map(doc):[m
[36m@@ -235,11 +234,14 @@[m [mdef build_item_wise_taxes_map(item_map, taxes_itemised_map, taxes_map, used_ecop[m
 			if not ecopart_account in item_wise_tax_detail_with_tva[vat_account]:[m
 				item_wise_tax_detail_with_tva[vat_account][ecopart_account] = {}[m
 [m
[31m-			if not ecopart_account in item_wise_tax_detail_before_tva:[m
[31m-				item_wise_tax_detail_before_tva[ecopart_account] = {}[m
[32m+[m			[32mif not vat_account in item_wise_tax_detail_before_tva:[m
[32m+[m				[32mitem_wise_tax_detail_before_tva[vat_account] = {}[m
[32m+[m
[32m+[m			[32mif not ecopart_account in item_wise_tax_detail_before_tva[vat_account]:[m
[32m+[m				[32mitem_wise_tax_detail_before_tva[vat_account][ecopart_account] = {}[m
 [m
 			for item_key in tax_itemised.keys():[m
[31m-				item_wise_tax_detail_before_tva[ecopart_account][item_key] = tax_itemised[item_key][m
[32m+[m				[32mitem_wise_tax_detail_before_tva[vat_account][ecopart_account][item_key] = tax_itemised[item_key][m
 				item_wise_tax_detail_with_tva[vat_account][ecopart_account][item_key] = [[m
 					tax_rate,[m
 					tax_itemised[item_key] * tax_rate / 100[m
[36m@@ -276,19 +278,29 @@[m [mdef create_update_ecopart_with_vat_taxes([m
 			if ([m
 					tax.charge_type == 'Actual'[m
 					and tax.account_head == ecopart_account[m
[31m-					and tax.description == ecopart_account[m
[32m+[m					[32mand tax.description == ecopart_account + "\n" + str(vat_account)[m
 			):[m
 				ecopart_tax = tax[m
 			elif ([m
 					tax.charge_type == 'On Previous Row Amount'[m
 					and tax.account_head == vat_account[m
[31m-					and tax.description == _('Eco Part VAT: {0}').format(str(ecopart_account))[m
[32m+[m					[32mand tax.description == _('Eco Part VAT: {0}').format(str(ecopart_account) + "\n" + str(vat_account))[m
 			):[m
 				ecopart_vat_tax = tax[m
 [m
[31m-		if ecopart_account in item_wise_tax_detail_before_tva:[m
[31m-			item_tax_wise = item_wise_tax_detail_before_tva[ecopart_account][m
[31m-			ecopart_tax = create_update_ecotax(doc, ecopart_account, ecopart_tax, item_tax_wise, total_tax)[m
[32m+[m		[32mif ([m
[32m+[m			[32mvat_account in item_wise_tax_detail_before_tva[m
[32m+[m			[32mand ecopart_account in item_wise_tax_detail_before_tva[vat_account][m
[32m+[m			[32mand ecopart_account in item_wise_tax_detail_with_tva[vat_account][m
[32m+[m		[32m):[m
[32m+[m			[32mitem_tax_wise = item_wise_tax_detail_before_tva[vat_account][ecopart_account][m
[32m+[m			[32mitem_code_2_keep = [][m
[32m+[m			[32mfor item_code in item_tax_wise:[m
[32m+[m				[32mif item_code in item_wise_tax_detail_with_tva[vat_account][ecopart_account].keys():[m
[32m+[m					[32mitem_code_2_keep.append(item_code)[m
[32m+[m
[32m+[m			[32mitem_tax_wise = {item_code : item_tax_wise[item_code] for item_code in item_code_2_keep}[m
[32m+[m			[32mecopart_tax = create_update_ecotax(doc, vat_account, ecopart_account, ecopart_tax, item_tax_wise, total_tax)[m
 [m
 		# Need to be done outside the for loop to get ecopart_tax.idx[m
 		if ([m
[36m@@ -312,21 +324,30 @@[m [mdef create_update_vat_taxes(doc, item_wise_tax_detail_standard_tva, vat_account)[m
 	vat_tax = None[m
 	for tax in doc.taxes:[m
 		if ([m
[31m-				tax.charge_type == 'On Net Total'[m
[32m+[m				[32mtax.charge_type == 'Actual'[m
 				and tax.account_head == vat_account[m
 				and vat_account in item_wise_tax_detail_standard_tva[m
 		):[m
 			vat_tax = tax[m
[32m+[m
 	item_tax_wise = item_wise_tax_detail_standard_tva[vat_account][m
[32m+[m
[32m+[m
 	tax_amount = 0[m
 	tax_rate = 0[m
[31m-	for item_code in item_tax_wise.keys():[m
[31m-		tax_amount += item_tax_wise[item_code][1][m
[31m-		tax_rate = item_tax_wise[item_code][0][m
[31m-	if not vat_tax:[m
[32m+[m	[32m# Update with new values[m
[32m+[m	[32mfor key, value in item_tax_wise.items():[m
[32m+[m		[32mtax_rate = value[0][m
[32m+[m		[32mtax_amount += value[1][m
[32m+[m
[32m+[m	[32mif vat_tax:[m
[32m+[m		[32mvat_tax.tax_amount = tax_amount[m
[32m+[m		[32mvat_tax.item_wise_tax_detail = json.dumps(item_tax_wise)[m
[32m+[m		[32mvat_tax.dont_recompute_tax = True[m
[32m+[m	[32melse:[m
 		vat_tax = frappe.get_doc({[m
 			'doctype': 'Sales Taxes and Charges',[m
[31m-			'charge_type': 'On Net Total',[m
[32m+[m			[32m'charge_type': 'Actual',[m
 			'description': str(vat_account),[m
 			'account_head': vat_account,[m
 			'parent': doc.name,[m
[36m@@ -337,14 +358,12 @@[m [mdef create_update_vat_taxes(doc, item_wise_tax_detail_standard_tva, vat_account)[m
 			'dont_recompute_tax': True,[m
 		})[m
 		doc.append("taxes", vat_tax)[m
[31m-	else:[m
[31m-		vat_tax.item_wise_tax_detail = json.dumps(item_tax_wise)[m
[31m-		vat_tax.dont_recompute_tax = True[m
 [m
 [m
[31m-def create_update_ecotax(doc, ecopart_account, ecopart_tax, item_tax_wise, total_tax):[m
[32m+[m[32mdef create_update_ecotax(doc, vat_account, ecopart_account, ecopart_tax, item_tax_wise, total_tax):[m
 	# Update existing tax rows if found[m
 	if ecopart_tax:[m
[32m+[m		[32m# frappe.throw(str(item_tax_wise) + "<br>" + str(ecopart_tax.item_wise_tax_detail))[m
 		# Load existing item_wise_tax_detail[m
 		existing_tax_detail = json.loads(ecopart_tax.item_wise_tax_detail) if ecopart_tax.item_wise_tax_detail else {}[m
 [m
[36m@@ -362,7 +381,7 @@[m [mdef create_update_ecotax(doc, ecopart_account, ecopart_tax, item_tax_wise, total[m
 		ecopart_tax = frappe.get_doc({[m
 			'doctype': 'Sales Taxes and Charges',[m
 			'charge_type': 'Actual',[m
[31m-			'description': ecopart_account,[m
[32m+[m			[32m'description': ecopart_account + "\n" + str(vat_account),[m
 			'account_head': ecopart_account,[m
 			'tax_amount': total_tax,[m
 			'parent': doc.name,[m
[36m@@ -403,7 +422,7 @@[m [mdef create_update_vat_on_ecotax([m
 		ecopart_vat_tax = frappe.get_doc({[m
 			'doctype': 'Sales Taxes and Charges',[m
 			'charge_type': 'On Previous Row Amount',[m
[31m-			'description': _('Eco Part VAT: {0}').format(str(ecopart_account)),[m
[32m+[m			[32m'description': _('Eco Part VAT: {0}').format(str(ecopart_account) + "\n" + str(vat_account)),[m
 			'account_head': vat_account,[m
 			'tax_amount': total_tax * tax_rate / 100,[m
 			'row_id': ecopart_tax_idx,[m
