# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import difflib

import frappe
import numpy as np
from frappe import _
from frappe.utils import add_days, flt, getdate
from frappe.utils.dateutils import parse_date

from erpnext import get_default_company
from erpnext.accounts.doctype.bank_transaction.bank_transaction import (
	get_bank_transaction_balance_on,
)

PARTY_FIELD = {
	"Payment Entry": "party",
	"Journal Entry": "party",
	"Sales Invoice": "customer",
	"Purchase Invoice": "supplier",
	"Expense Claim": "employee_name",
}

PARTY_TYPES = {
	"Sales Invoice": "Customer",
	"Purchase Invoice": "Supplier",
	"Expense Claim": "Employee",
}


@frappe.whitelist()
def get_linked_payments(bank_transactions, document_type, match=True):
	bank_transaction_match = BankTransactionMatch(bank_transactions, document_type, match)
	return bank_transaction_match.get_linked_payments()


class BankTransactionMatch:
	def __init__(self, bank_transactions, document_type, match=True):
		self.bank_transactions = frappe.parse_json(bank_transactions) or []
		self.document_type = document_type
		self.match = False if match == "false" else True
		self.amount = sum([x.get("amount") for x in self.bank_transactions]) or 0
		self.currency = self.bank_transactions[0]["currency"] if self.bank_transactions else None
		self.bank_account = self.bank_transactions[0]["bank_account"] if self.bank_transactions else None
		self.account = (
			frappe.db.get_value("Bank Account", self.bank_account, "account") if self.bank_account else None
		)
		self.company = (
			frappe.db.get_value("Bank Account", self.bank_account, "company")
			if self.bank_account
			else get_default_company()
		)

	def get_linked_payments(self):
		if not self.bank_transactions:
			return []

		documents = self.get_linked_documents()

		if not documents or not self.match:
			return sorted(
				[i for n, i in enumerate(documents) if i not in documents[n + 1 :]],
				key=lambda x: x.get("posting_date", x.get("reference_date")),
				reverse=True,
			)

		# Check if document with a matching amount (+- 10%) exists
		amount_matches = self.check_matching_amounts(documents)
		if amount_matches and len(amount_matches) == 1:
			return [dict(x, **{"vgtSelected": True}) for x in amount_matches]

		# Get similar bank transactions from history
		similar_transactions_matches = self.get_similar_transactions_references()

		result = amount_matches + similar_transactions_matches
		output = sorted(
			[i for n, i in enumerate(result) if i not in result[n + 1 :]],
			key=lambda x: x.get("posting_date", x.get("reference_date")),
			reverse=True,
		)
		return (
			[dict(x, **{"vgtSelected": True}) for x in output]
			if len(output) == 1
			else self.check_matching_dates(output)
		)

	def get_linked_documents(self, document_names=None, unreconciled=True, filters=None):
		query_filters = {"docstatus": 1, "company": self.company}
		query_or_filters = {}

		if self.document_type == "Journal Entry":
			return self.get_linked_journal_entries(document_names, unreconciled, filters)
		elif self.document_type not in ["Expense Claim", "Payment Entry"]:
			query_filters.update({"currency": self.currency})

		if filters:
			query_filters.update(filters)

		if unreconciled and self.document_type == "Expense Claim":
			query_filters.update({"total_sanctioned_amount": ("!=", 0)})
			query_or_filters.update({"unreconciled_amount": ("!=", 0), "total_amount_reimbursed": ("=", 0)})
		elif unreconciled and self.document_type in ["Sales Invoice", "Purchase Invoice"]:
			query_or_filters.update({"unreconciled_amount": ("!=", 0), "outstanding_amount": (">", 0)})
		elif unreconciled:
			query_filters.update({"unreconciled_amount": ("!=", 0)})

		if document_names:
			query_filters.update({"name": ("in", document_names)})

		query_result = frappe.get_list(
			self.document_type, filters=query_filters, or_filters=query_or_filters, fields=["*"]
		)

		return self.get_filtered_results(query_result)

	def get_filtered_results(self, query_result):
		filtered_result = []
		party_field = PARTY_FIELD.get(self.document_type)
		reference_field = self.get_reference_field()
		date_field = self.get_reference_date_field()

		if self.document_type == "Payment Entry":
			for result in query_result:
				if (
					result.get("paid_from_account_currency") == self.currency
					and result.get("paid_from") == self.account
				):
					filtered_result.append(
						dict(
							result,
							**{
								"amount": result.get("unreconciled_from_amount", 0) * -1,
								"party": result.get(party_field),
								"reference_date": result.get(date_field),
								"reference_string": f'{result.get("name")}: {result.get(reference_field)}',
								"unreconciled_amount": result.get("unreconciled_from_amount", 0),
							},
						)
					)

				elif (
					result.get("paid_to_account_currency") == self.currency
					and result.get("paid_to") == self.account
				):
					filtered_result.append(
						dict(
							result,
							**{
								"amount": result.get("unreconciled_to_amount", 0),
								"party": result.get(party_field),
								"reference_date": result.get(date_field),
								"reference_string": f'{result.get("name")}: {result.get(reference_field)}',
								"unreconciled_amount": result.get("unreconciled_to_amount", 0),
							},
						)
					)

		elif self.document_type == "Purchase Invoice":
			return [
				dict(
					x,
					**{
						"amount": (
							flt(x.get("unreconciled_amount", 0))
							if flt(x.get("unreconciled_amount")) > 0
							else flt(x.get("outstanding_amount", 0))
						)
						if flt(x.get("is_return")) == 1
						else (
							(
								flt(x.get("unreconciled_amount", 0))
								if flt(x.get("unreconciled_amount")) > 0
								else flt(x.get("outstanding_amount", 0))
							)
							* -1
						),
						"party": x.get(party_field),
						"reference_date": x.get(date_field),
						"reference_string": f'{x.get("name")}: {x.get(reference_field)}',
					},
				)
				for x in query_result
			]

		elif self.document_type == "Sales Invoice":
			return [
				dict(
					x,
					**{
						"amount": (
							(
								flt(x.get("unreconciled_amount", 0))
								if flt(x.get("unreconciled_amount")) > 0
								else flt(x.get("outstanding_amount", 0))
							)
							* -1
						)
						if flt(x.get("is_return")) == 1
						else (
							flt(x.get("unreconciled_amount", 0))
							if flt(x.get("unreconciled_amount")) > 0
							else flt(x.get("outstanding_amount", 0))
						),
						"party": x.get(party_field),
						"reference_date": x.get(date_field),
						"reference_string": f'{x.get("name")}: {x.get(reference_field)}',
					},
				)
				for x in query_result
			]

		elif self.document_type == "Expense Claim":
			return [
				dict(
					x,
					**{
						"amount": x.get("total_amount_reimbursed", 0) - x.get("total_sanctioned_amount", 0),
						"party": x.get(party_field),
						"reference_date": x.get(date_field),
						"reference_string": f'{x.get("name")}: {x.get(reference_field)}',
					},
				)
				for x in query_result
			]

		else:
			filtered_result = query_result

		return filtered_result

	def get_linked_journal_entries(self, document_names=None, unreconciled=True, filters=None):
		child_query_filters = {
			"account_currency": self.currency,
			"account": self.account,
			"docstatus": 1,
		}
		parent_query_filters = {"company": self.company}

		if unreconciled:
			parent_query_filters.update({"unreconciled_amount": ("!=", 0)})

		if document_names:
			parent_query_filters.update({"name": ("in", document_names)})
		else:
			bank_entries = [
				x.get("parent")
				for x in frappe.get_all(
					"Journal Entry Account", filters=child_query_filters, fields=["parent"]
				)
			]
			parent_query_filters.update({"name": ("in", bank_entries)})

		parent_query_result = frappe.get_list(
			"Journal Entry",
			filters=parent_query_filters,
			fields=[
				"name",
				"posting_date",
				"cheque_no",
				"cheque_date",
				"unreconciled_amount",
				"remark",
				"user_remark",
			],
		)
		parent_map = {x.get("name"): x for x in parent_query_result}

		child_query_filters.update(
			{"parenttype": "Journal Entry", "parent": ("in", [x.name for x in parent_query_result])}
		)

		if filters:
			child_query_filters.update(filters)

		party_query_result = frappe.get_all(
			"Journal Entry Account", filters=child_query_filters, fields=["*"]
		)

		result = [
			dict(
				x,
				**{
					"name": parent_map.get(x.get("parent"), {}).get("name"),
					"amount": x.get("unreconciled_amount"),
					"posting_date": parent_map.get(x.get("parent"), {}).get("posting_date"),
					"reference_date": parent_map.get(x.get("parent"), {}).get("cheque_date"),
					"reference_string": parent_map.get(x.get("parent"), {}).get("cheque_no")
					or parent_map.get(x.get("parent"), {}).get("remark")
					or parent_map.get(x.get("parent"), {}).get("user_remark"),
					"unreconciled_amount": x.get("unreconciled_amount"),
				},
			)
			for x in party_query_result
		]

		return [x for x in result if x.get("amount") and x.get("name")]

	def get_amount_field(self, debit_or_credit="debit"):
		return {
			"Payment Entry": "paid_amount",
			"Journal Entry": "debit_in_account_currency"
			if debit_or_credit == "debit"
			else "credit_in_account_currency",
			"Sales Invoice": "outstanding_amount",
			"Purchase Invoice": "outstanding_amount",
			"Expense Claim": "total_sanctioned_amount",
		}.get(self.document_type)

	def get_reference_date_field(self):
		return {
			"Payment Entry": "reference_date",
			"Journal Entry": "cheque_date",
			"Sales Invoice": "due_date",
			"Purchase Invoice": "due_date",
			"Expense Claim": "posting_date",
		}.get(self.document_type)

	def get_reference_field(self):
		return {
			"Payment Entry": "reference_no",
			"Journal Entry": "cheque_no",
			"Sales Invoice": "remarks",
			"Purchase Invoice": "remarks",
			"Expense Claim": "remark",
		}.get(self.document_type)

	def check_matching_amounts(self, documents):
		amount_field = self.get_amount_field("debit" if self.amount > 0 else "credit")
		return [x for x in documents if flt(abs(self.amount)) == flt(x.get(amount_field))]

	def check_matching_dates(self, output):
		if not output:
			return []

		comparison_date = self.bank_transactions[0].get("date")
		description = self.bank_transactions[0].get("description")

		if description:
			output = sorted(
				output,
				key=lambda doc: difflib.SequenceMatcher(
					lambda doc: doc == " ", str(doc.get("party")), description
				).ratio(),
				reverse=True,
			)

		date_field = self.get_reference_date_field()
		closest = min(
			output[:10],
			key=lambda x: abs(getdate(x.get(date_field)) - getdate(parse_date(comparison_date))),
		)

		return [
			dict(x, **{"vgtSelected": True}) if x.get("name") == closest.get("name") else x for x in output
		]

	def get_similar_transactions_references(self):
		already_reconciled_matches = self.get_already_reconciled_matches()
		references = self.get_similar_documents(already_reconciled_matches)
		return self.get_similar_transactions_based_on_history(references)

	def get_similar_transactions_based_on_history(self, references):
		descriptions = self.get_description_and_party(references)

		query_filters = {descriptions.get("party_field"): ["in", descriptions.get("party")]}

		return self.get_linked_documents(unreconciled=True, filters=query_filters)

	def get_description_and_party(self, references):
		output = {
			"party": set(),
			"description": set(),
			"party_field": PARTY_FIELD.get(self.document_type),
			"description_field": self.get_reference_field(),
		}

		for reference in references:
			output["description"].add(reference.get(output["description_field"]))

			if reference.get("doctype") == "Journal Entry":
				je_parties = set(
					[
						x.party
						for x in frappe.get_all(
							"Journal Entry Account",
							filters={
								"parent": reference.get("name"),
								"parenttype": reference.get("doctype"),
								"party_type": ["is", "set"],
							},
							fields=["party"],
						)
					]
				)

				output["party"].update(je_parties)

			else:
				output["party"].add(reference.get(output["party_field"]))

		return output

	def get_already_reconciled_matches(self):
		reconciled_bank_transactions = get_reconciled_bank_transactions()

		selection = []
		for transaction in self.bank_transactions:
			for bank_transaction in reconciled_bank_transactions:
				if transaction.get("description") and bank_transaction.get("description"):
					seq = difflib.SequenceMatcher(
						lambda x: x == " ",
						transaction.get("description", ""),
						bank_transaction.get("description", ""),
					)

					if seq.ratio() > 0.6:
						bank_transaction["ratio"] = seq.ratio()
						selection.append(bank_transaction)

		return [x.get("name") for x in selection]

	def get_similar_documents(self, transactions):
		payments_references = [
			x.get("payment_entry")
			for x in frappe.get_list(
				"Bank Transaction Payments",
				filters={
					"parent": ("in", transactions),
					"parenttype": ("=", "Bank Transaction"),
					"payment_document": self.document_type,
				},
				fields=["payment_document", "payment_entry"],
				parent_doctype="Bank Transaction",
			)
		]
		return self.get_linked_documents(document_names=payments_references, unreconciled=False)


def get_reconciled_bank_transactions():
	return frappe.get_list(
		"Bank Transaction",
		filters={"allocated_amount": (">", 0), "docstatus": 1},
		fields=["name", "description"],
	)


@frappe.whitelist()
def get_statement_chart(account, start_date, end_date):
	transactions = frappe.get_all(
		"Bank Transaction",
		filters={
			"docstatus": 1,
			"date": ["between", [getdate(start_date), getdate(end_date)]],
			"bank_account": account,
		},
		fields=[
			"sum(credit)-sum(debit) as amount",
			"date",
			"currency",
			"sum(unallocated_amount) as unallocated_amount",
		],
		group_by="date",
		order_by="date ASC",
	)

	balance_before = get_bank_transaction_balance_on(account, add_days(getdate(start_date), -1))

	if not transactions or not balance_before:
		return {}

	symbol = (
		frappe.db.get_value("Currency", transactions[0].currency, "symbol", cache=True)
		or transactions[0].currency
	)

	previous_unallocation = frappe.get_all(
		"Bank Transaction",
		filters={"docstatus": 1, "date": ("<", getdate(start_date)), "bank_account": account},
		fields=["sum(unallocated_amount) as unallocated_amount"],
	)

	dates = [add_days(getdate(start_date), -1)]
	daily_balance = [balance_before.get("balance")]
	unallocated_amount = [
		previous_unallocation[0]["unallocated_amount"] if previous_unallocation else 0
	]

	for transaction in transactions:
		dates.append(transaction.date)
		daily_balance.append(transaction.amount)
		unallocated_amount.append(transaction.unallocated_amount)

	bank_balance = np.round(np.cumsum(daily_balance), decimals=2)
	mean_value = np.mean(bank_balance)

	data = {
		"title": _("Bank Balance") + " (" + symbol + ")",
		"data": {
			"datasets": [
				{"name": _("Bank Balance"), "values": bank_balance},
				{"name": _("Unallocated Amount"), "chartType": "bar", "values": unallocated_amount},
			],
			"labels": dates,
			"yMarkers": [
				{"label": _("Average balance"), "value": mean_value, "options": {"labelPos": "left"}}
			],
		},
		"type": "line",
		"colors": ["blue", "green"],
		"lineOptions": {"hideDots": 1},
	}

	return data


@frappe.whitelist()
def get_initial_balance(account, start_date):
	return get_bank_transaction_balance_on(account, add_days(getdate(start_date), -1))


@frappe.whitelist()
def get_final_balance(account, end_date):
	return get_bank_transaction_balance_on(account, getdate(end_date))
