# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import arrow
import frappe
from frappe.utils import getdate

from erpnext.accounts.page.bank_reconciliation.bank_reconciliation import BankReconciliation


def reconcile_stripe_payouts(bank_transactions):
	stripe_transactions = [
		transaction
		for transaction in bank_transactions
		if "stripe" in (transaction.get("description") or "").lower()
	]
	if not stripe_transactions:
		return

	stripe_accounts = frappe.get_list(
		"Stripe Settings", {"bank_account": bank_transactions[0].get("bank_account")}
	)
	if not stripe_accounts:
		return

	_reconcile_stripe_payouts(bank_transactions=stripe_transactions, stripe_accounts=stripe_accounts)


def _reconcile_stripe_payouts(bank_transactions, stripe_accounts):
	reconciled_transactions = []
	for stripe_account in stripe_accounts:
		stripe_settings = frappe.get_doc("Stripe Settings", stripe_account.name)

		for bank_transaction in bank_transactions:
			if bank_transaction.get("name") not in reconciled_transactions:
				bank_reconciliation = StripeReconciliation(stripe_settings, bank_transaction)
				bank_reconciliation.reconcile()
				if bank_reconciliation.documents:
					reconciled_transactions.append(bank_transaction.get("name"))


class StripeReconciliation:
	def __init__(self, stripe_settings, bank_transaction):
		self.stripe_settings = stripe_settings
		self.bank_transaction = bank_transaction
		self.date = self.bank_transaction.get("date")
		self.payouts = []
		self.filtered_payout = {}
		self.documents = []

	def reconcile(self):
		self.get_payouts_and_transactions()
		self.match_transactions_with_payouts()
		if not self.filtered_payout:
			return

		self.get_invoices_references()
		self.get_corresponding_documents()
		if self.documents:
			BankReconciliation([self.bank_transaction], self.documents).reconcile()

	def get_payouts_and_transactions(self):
		self.list_stripe_payouts()
		self.payouts = [dict(x, **{"transactions": []}) for x in self.payouts]

		for payout in self.payouts:
			self.list_stripe_charges(payout)

	def list_stripe_payouts(self):
		has_more = True
		starting_after = None
		while has_more:
			result = self.stripe_settings.stripe.Payout.list(
				arrival_date=arrow.get(getdate(self.date)).timestamp, starting_after=starting_after
			)
			if hasattr(result, "data"):
				self.payouts.extend(result.data)

			if not result.has_more:
				has_more = False
			else:
				starting_after = result.data[-1].id

	def list_stripe_charges(self, payout):
		has_more = True
		starting_after = None
		while has_more:
			result = self.stripe_settings.stripe.BalanceTransaction.list(
				payout=payout.get("id"), starting_after=starting_after
			)
			if hasattr(result, "data"):
				payout["transactions"].extend(result.data)

			if not result.has_more:
				has_more = False
			else:
				starting_after = result.data[-1].id

	def match_transactions_with_payouts(self):
		for payout in self.payouts:
			if (self.bank_transaction.get("currency").lower() == payout.get("currency")) and (
				(
					(self.bank_transaction.get("credit", 0) - self.bank_transaction.get("debit", 0)) * 100
					- payout.get("amount")
				)
				<= 0.01
			):
				self.filtered_payout = payout
				break

	def get_invoices_references(self):
		for transaction in self.filtered_payout.get("transactions"):
			if transaction.get("type") == "charge":
				transaction["charge"] = self.stripe_settings.stripe.Charge.retrieve(transaction.get("source"))

	def get_corresponding_documents(self):
		for transaction in self.filtered_payout.get("transactions"):
			if transaction.get("type") == "charge":

				for doctype in ["Payment Entry", "Sales Invoice", "Purchase Invoice", "Expense Claim"]:
					reference_field = self.get_reference_field(doctype)
					documents = [
						dict(x, **{"doctype": doctype})
						for x in frappe.get_all(
							doctype,
							filters={"unreconciled_amount": ("!=", 0), "docstatus": 1},
							or_filters=[
								{reference_field: ("like", transaction.get("charge", {}).get("id"))},
								{reference_field: ("like", transaction.get("charge", {}).get("invoice"))},
								{reference_field: ("like", transaction.get("charge", {}).get("payment_intent"))},
							],
							fields=["*"],
						)
					]
					self.documents.extend(documents)

	def get_reference_field(self, doctype):
		return {
			"Payment Entry": "reference_no",
			"Journal Entry": "cheque_no",
			"Sales Invoice": "remarks",
			"Purchase Invoice": "remarks",
			"Expense Claim": "remark",
		}.get(doctype)
