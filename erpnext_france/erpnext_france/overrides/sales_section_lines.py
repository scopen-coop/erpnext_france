# Copyright (c) 2026, Scopen and contributors
# For license information, please see license.txt
"""
Gestion des lignes de structure (titres de section et sous-totaux) sur les
documents Quotation / Sales Order / Sales Invoice / Delivery Note.

Une ligne du child table `items` peut prendre 3 valeurs pour `ef_line_type` :
    - "Item"          : ligne d'article classique (defaut)
    - "Section Header": titre de section, n'entre pas dans les totaux
    - "Subtotal"      : ligne affichant la somme de la section precedente

Pour eviter d'impacter le grand_total, on force qty/rate a 0 sur ces lignes
AVANT le calcul des totaux ERPNext (hook `before_validate`).
Le sous-total est ensuite ecrit dans `ef_section_amount` pendant `validate`.
"""

import frappe

# Types de lignes consideres comme "structurelles" (hors calcul des totaux)
SECTION_TYPES = ("Section Header", "Subtotal")


def before_validate(doc, method=None):
	"""Force qty/rate/discount a 0 sur les lignes structurelles.

	Appele avant le calcul ERPNext des totaux : le grand_total ne sera donc
	pas pollue meme si l'utilisateur a saisi des valeurs sur ces lignes.
	"""
	for item in doc.get("items") or []:
		line_type = item.get("ef_line_type") or "Item"
		if line_type in SECTION_TYPES:
			item.qty = 0
			item.rate = 0
			item.amount = 0
			# Securite : neutraliser tout calcul derive (remise, marge)
			if hasattr(item, "discount_amount"):
				item.discount_amount = 0
			if hasattr(item, "discount_percentage"):
				item.discount_percentage = 0
			if hasattr(item, "margin_rate_or_amount"):
				item.margin_rate_or_amount = 0
			if hasattr(item, "stock_qty"):
				item.stock_qty = 0


def validate(doc, method=None):
	"""Calcule `ef_section_amount` pour chaque ligne Subtotal.

	Algorithme : on parcourt les lignes dans l'ordre. Un cumul est remis a 0
	a chaque Section Header (ou demarre a 0 au debut du document). Chaque
	ligne Item ajoute son `amount` au cumul. Chaque Subtotal recoit la valeur
	courante du cumul.
	"""
	running_total = 0.0

	for item in doc.get("items") or []:
		line_type = item.get("ef_line_type") or "Item"

		if line_type == "Section Header":
			running_total = 0.0
			item.ef_section_amount = 0
		elif line_type == "Subtotal":
			item.ef_section_amount = running_total
		else:
			running_total += float(item.get("amount") or 0)
