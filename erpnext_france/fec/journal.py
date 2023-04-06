# -*- coding: utf-8 -*-
# Copyright (c) 2017, Britlog and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist(allow_guest=False)
def get_journal_code(mode_of_payment, company):
	"""Get naming_series (=journal code) from mode of payment"""

	journal_code = frappe.db.get_value("Mode of Payment Account", {"parent": mode_of_payment, "company": company}, "journal_label")

	return journal_code
