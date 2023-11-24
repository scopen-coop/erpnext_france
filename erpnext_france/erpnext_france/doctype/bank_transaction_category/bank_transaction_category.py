# Copyright (c) 2022, Dokos SAS and contributors
# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.nestedset import NestedSet, get_root_of

class BankTransactionCategory(NestedSet):
	nsm_parent_field = 'parent_bank_transaction_category'
	def validate(self):
		if not self.parent_bank_transaction_category:
			self.parent_bank_transaction_category = get_root_of("Bank Transaction Category")

def on_doctype_update():
	frappe.db.add_index("Bank Transaction Category", ["lft", "rgt"])
