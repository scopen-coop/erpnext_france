import unittest

import erpnext
import frappe


@erpnext.allow_regional
def test_method():
	return "original"


class TestInit(unittest.TestCase):
	def test_regional_overrides(self):
		frappe.flags.country = "France"
		self.assertEqual(test_method(), "original")
