# Copyright (c) 2026, Scopen and contributors
# For license information, please see license.txt
"""Tests des lignes de structure (Section Header / Subtotal) sur Quotation."""

import unittest

import frappe
from frappe.utils import flt


class TestSectionLines(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		# Recupere un Customer et un Item de vente existants pour eviter de creer
		# des fixtures supplementaires (le test n'a pas besoin de donnees specifiques).
		cls.customer = frappe.db.get_value("Customer", {"disabled": 0}, "name")
		cls.item_code = frappe.db.get_value(
			"Item", {"is_sales_item": 1, "disabled": 0}, "name"
		)

	def setUp(self):
		if not (self.customer and self.item_code):
			self.skipTest("Pas de Customer ou Item disponible pour les tests")

	def _build_quotation(self):
		"""Construit un Quotation avec 2 sections et 3 articles."""
		return frappe.get_doc({
			"doctype": "Quotation",
			"quotation_to": "Customer",
			"party_name": self.customer,
			"items": [
				# Section 1: Main d'oeuvre — qty/rate non-zero, doivent etre forces a 0
				{
					"ef_line_type": "Section Header",
					"ef_section_label": "Main d'oeuvre",
					"qty": 5,
					"rate": 99,
				},
				{"item_code": self.item_code, "qty": 2, "rate": 100},
				{"item_code": self.item_code, "qty": 1, "rate": 50},
				{
					"ef_line_type": "Subtotal",
					"ef_section_label": "Sous-total main d'oeuvre",
				},
				# Section 2: Materiaux
				{"ef_line_type": "Section Header", "ef_section_label": "Materiaux"},
				{"item_code": self.item_code, "qty": 3, "rate": 30},
				{
					"ef_line_type": "Subtotal",
					"ef_section_label": "Sous-total materiaux",
				},
			],
		})

	def test_section_lines_qty_rate_forced_to_zero(self):
		"""Une ligne Section Header / Subtotal a bien qty=0, rate=0, amount=0 apres save."""
		quotation = self._build_quotation()
		quotation.insert(ignore_permissions=True)

		try:
			for item in quotation.items:
				if item.ef_line_type in ("Section Header", "Subtotal"):
					self.assertEqual(flt(item.qty), 0, f"qty doit etre 0 sur {item.ef_line_type}")
					self.assertEqual(flt(item.rate), 0, f"rate doit etre 0 sur {item.ef_line_type}")
					self.assertEqual(flt(item.amount), 0, f"amount doit etre 0 sur {item.ef_line_type}")
		finally:
			quotation.delete()

	def test_section_amount_computed_correctly(self):
		"""ef_section_amount calcule correctement sur chaque ligne Subtotal."""
		quotation = self._build_quotation()
		quotation.insert(ignore_permissions=True)

		try:
			# items[3] = Subtotal Main d'oeuvre : 2*100 + 1*50 = 250
			self.assertEqual(flt(quotation.items[3].ef_section_amount), 250.0)
			# items[6] = Subtotal Materiaux : 3*30 = 90
			self.assertEqual(flt(quotation.items[6].ef_section_amount), 90.0)
		finally:
			quotation.delete()

	def test_grand_total_excludes_section_lines(self):
		"""Le grand_total n'inclut pas les lignes Section Header / Subtotal."""
		quotation = self._build_quotation()
		quotation.insert(ignore_permissions=True)

		try:
			# Total attendu : 250 (main d'oeuvre) + 90 (materiaux) = 340
			# (en l'absence de taxes, net_total == total HT == grand_total)
			self.assertEqual(flt(quotation.net_total), 340.0)
		finally:
			quotation.delete()


def _run():
	"""Permet `bench run-tests --module erpnext_france.tests.test_section_lines`."""
	unittest.main()


if __name__ == "__main__":
	_run()
