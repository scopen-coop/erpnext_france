# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import re

import frappe
from frappe import _

import erpnext
from erpnext.accounts.page.bank_reconciliation.bank_reconciliation import BankReconciliation
from erpnext.accounts.page.bank_reconciliation.gocardless_reconciliation import (
	reconcile_gocardless_payouts,
)
from erpnext.accounts.page.bank_reconciliation.stripe_reconciliation import (
	reconcile_stripe_payouts,
)


@frappe.whitelist()
def auto_bank_reconciliation(bank_transactions):
	_reconcile_transactions(bank_transactions)


def _reconcile_transactions(bank_transactions):
	bank_transactions = frappe.parse_json(bank_transactions) or []
	if not bank_transactions:
		frappe.throw(_("Please select a period with at least one transaction to reconcile"))

	for bank_transaction in bank_transactions:
		if not bank_transaction.get("amount"):
			continue

		if frappe.get_hooks("auto_reconciliation_methods"):
			for hook in frappe.get_hooks("auto_reconciliation_methods"):
				frappe.get_attr(hook)(bank_transaction)
		else:
			bank_reconciliation = AutoBankReconciliation(bank_transaction)
			bank_reconciliation.reconcile()

	reconcile_stripe_payouts(bank_transactions)
	reconcile_gocardless_payouts(bank_transactions)


class AutoBankReconciliation:
	def __init__(self, bank_transaction):
		self.bank_transaction = bank_transaction
		self.documents = []

	def reconcile(self):
		# Reconcile by document name in references
		self.reconciliation_by_id()

		self.purchase_invoices_reconciliation()

		# Call regional reconciliation features
		regional_reconciliation(self)

		if self.documents:
			BankReconciliation(
				[self.bank_transaction], list({d["name"]: d for d in self.documents}.values())
			).reconcile()

	def reconciliation_by_id(self):
		matching_names = set()
		references = [
			x.get("name")
			for x in frappe.db.sql("""SELECT name FROM `tabSeries`""", as_dict=True)
			if x.get("name")
		]
		self.check_transaction_references(references, matching_names)
		if matching_names:
			self.get_corresponding_documents(matching_names)

	def purchase_invoices_reconciliation(self):
		matching_bill_no = set()
		references = frappe.get_all(
			"Purchase Invoice",
			filters={"docstatus": 1, "outstanding_amount": ("!=", 0), "bill_no": ("is", "set")},
			pluck="bill_no",
		)
		self.check_transaction_references(references, matching_bill_no)
		if matching_bill_no:
			matching_names = [{"bill_no": bill_no} for bill_no in matching_bill_no]
			self.get_corresponding_documents(matching_names)

	def check_transaction_references(self, references, output):
		for prefix in references:
			for reference in [
				self.bank_transaction.get("reference_number"),
				self.bank_transaction.get("description"),
			]:
				if reference:
					# TODO: get multiple references separated by a comma or a space
					search_regex = r"{0}[^ ]*".format(prefix)
					match = re.findall(search_regex, reference)
					if match:
						for m in match:
							output.add(m)

	def get_corresponding_documents(self, matching_names):
		for matching_name in matching_names:
			corresponding_payment_entry = self.get_corresponding_payment_entries(matching_name)
			if corresponding_payment_entry:
				self.documents.append(corresponding_payment_entry.as_dict())
				break
			else:
				for dt in ["Sales Invoice", "Purchase Invoice"]:
					if frappe.db.exists(dt, matching_name):
						doc = frappe.get_doc(dt, matching_name)
						if doc.outstanding_amount == 0:
							for payment_entry in frappe.get_all(
								"Payment Entry Reference",
								filters={"reference_doctype": doc.doctype, "reference_name": doc.name},
								pluck="parent",
							):
								corresponding_payment_entry = self.get_corresponding_payment_entries(payment_entry)
								if corresponding_payment_entry:
									self.documents.append(corresponding_payment_entry.as_dict())
									break
						else:
							self.documents.append(doc.as_dict())
							break

	def get_corresponding_payment_entries(self, matching_name):
		if frappe.db.exists("Payment Entry", matching_name):
			doc = frappe.get_doc("Payment Entry", matching_name)
			if doc.docstatus == 1 and doc.status == "Unreconciled":
				return doc


# Used for regional overrides
@erpnext.allow_regional
def regional_reconciliation(auto_bank_reconciliation):
	pass
