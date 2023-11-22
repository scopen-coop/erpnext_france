# -*- coding: utf-8 -*-
# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import re

import frappe
from payments.payment_gateways.doctype.gocardless_settings.api import GoCardlessPayouts

from erpnext_france.erpnext_france.page.bank_reconciliation.bank_reconciliation import BankReconciliation


def reconcile_gocardless_payouts(bank_transactions):
	gocardless_transactions = [
		transaction
		for transaction in bank_transactions
		if "gocardless" in transaction.get("description").lower()
	]
	if not gocardless_transactions:
		return

	gocardless_accounts = frappe.get_list(
		"GoCardless Settings", {"bank_account": bank_transactions[0].get("bank_account")}
	)
	if not gocardless_accounts:
		return

	_reconcile_gocardless_payouts(
		bank_transactions=gocardless_transactions, gocardless_accounts=gocardless_accounts
	)


def _reconcile_gocardless_payouts(bank_transactions, gocardless_accounts):
	reconciled_transactions = []
	for gocardless_account in gocardless_accounts:
		gocardless_settings = frappe.get_doc("GoCardless Settings", gocardless_account.name)

		for bank_transaction in bank_transactions:
			if bank_transaction.get("name") not in reconciled_transactions:
				bank_reconciliation = GoCardlessReconciliation(gocardless_settings, bank_transaction)
				bank_reconciliation.reconcile()
				if bank_reconciliation.documents:
					reconciled_transactions.append(bank_transaction.get("name"))


class GoCardlessReconciliation:
	def __init__(self, gocardless_settings, bank_transaction):
		self.gocardless_settings = gocardless_settings
		self.bank_transaction = bank_transaction
		self.date = self.bank_transaction.get("date")
		self.payouts = []
		self.filtered_payout = {}
		self.documents = []

	def reconcile(self):
		self.get_payouts_and_transactions()
		self.get_payment_references()

		if self.documents:
			BankReconciliation([self.bank_transaction], self.documents).reconcile()

	def get_payouts_and_transactions(self):
		found_reference = re.search(r"GoCardless(.*?) CT", self.bank_transaction.get("description"))
		if found_reference:
			reference = found_reference.group(1).strip()
			payouts = GoCardlessPayouts(self.gocardless_settings).get_list(reference=reference)

			for payout in payouts.records:
				items = self.gocardless_settings.client.payout_items.list(params=dict(payout=payout.id))
				for item in items.records:
					if item.type == "payment_paid_out":
						self.payouts.append(item)

	def get_payment_references(self):
		for payout in self.payouts:
			links = getattr(payout, "links") or {}
			payment = getattr(links, "payment")

			payment_entry = frappe.db.get_value(
				"Payment Entry", dict(reference_no=payment, docstatus=1, status=("=", "Unreconciled"))
			)
			if payment_entry:
				self.documents.append(frappe.get_doc("Payment Entry", payment_entry).as_dict())
