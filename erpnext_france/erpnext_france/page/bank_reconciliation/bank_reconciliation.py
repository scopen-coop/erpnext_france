# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import flt, getdate
from frappe.utils.dateutils import parse_date

from erpnext.accounts.doctype.bank_account.bank_account import get_party_bank_account
from erpnext.accounts.doctype.invoice_discounting.invoice_discounting import (
	get_party_account_based_on_invoice_discounting,
)
from erpnext.accounts.utils import get_account_currency

PARTY_FIELD = {
	"Payment Entry": "party",
	"Journal Entry": "party",
	"Sales Invoice": "customer",
	"Purchase Invoice": "supplier",
	"Expense Claim": "employee",
}

PARTY_TYPES = {
	"Sales Invoice": "Customer",
	"Purchase Invoice": "Supplier",
	"Expense Claim": "Employee",
}


@frappe.whitelist()
def reconcile(bank_transactions, documents):
	bank_reconciliation = BankReconciliation(bank_transactions, documents)
	bank_reconciliation.reconcile()


class BankReconciliation:
	def __init__(self, bank_transactions, documents):
		self.bank_transactions = frappe.parse_json(bank_transactions)
		self.documents = frappe.parse_json(documents)

		if not self.bank_transactions or not self.documents:
			frappe.throw(_("Please select at least one bank transaction and one document to reconcile"))

		self.reconciliation_doctype = self.documents[0]["doctype"]
		self.party = None
		self.party_account = None
		self.party_type = PARTY_TYPES.get(self.reconciliation_doctype)
		self.company = None
		self.cost_center = None
		self.mode_of_payment = None
		self.payment_entries = []

	def check_unique_values(self):
		self.check_party()
		self.check_party_account()
		self.check_field_uniqueness("company", _("company"))
		self.check_field_uniqueness("cost_center", _("cost center"))
		self.check_field_uniqueness("mode_of_payment", _("mode of payment"))

	def check_party(self):
		party = set([x.get(PARTY_FIELD.get(self.reconciliation_doctype)) for x in self.documents])
		if not party or len(party) > 1:
			frappe.throw(_("Please select documents linked to the same party"))
		else:
			self.party = next(iter(party))

	def check_party_account(self):
		if self.reconciliation_doctype == "Sales Invoice":
			party_account = set(
				[
					get_party_account_based_on_invoice_discounting(doc.get("name")) or doc.get("debit_to")
					for doc in self.documents
				]
			)
		elif self.reconciliation_doctype == "Purchase Invoice":
			party_account = set([doc.get("credit_to") for doc in self.documents])
		elif self.reconciliation_doctype == "Employee Advance":
			party_account = set([doc.get("advance_account") for doc in self.documents])
		elif self.reconciliation_doctype == "Expense Claim":
			party_account = set([doc.get("payable_account") for doc in self.documents])

		if not party_account or len(party_account) > 1:
			frappe.throw(_("Please select documents linked to the same party account"))
		else:
			self.party_account = next(iter(party_account))

	def check_field_uniqueness(self, fielname, label):
		value = set([x.get(fielname) for x in self.documents])

		if not value or len(value) > 1:
			frappe.throw(_("Please select documents linked to the same {0}").format(label))
		else:
			setattr(self, fielname, next(iter(value)))

	def reconcile(self):
		if self.reconciliation_doctype in [
			"Sales Invoice",
			"Purchase Invoice",
			"Expense Claim",
		] and not (self.documents[0].get("is_pos") or self.documents[0].get("is_paid")):
			self.check_unique_values()
			self.make_payment_entries()
			self.reconcile_created_payments()

		elif len(self.bank_transactions) > 1:
			self.reconcile_multiple_transactions_with_one_document()
		elif len(self.documents) >= 1:
			self.reconcile_one_transaction_with_multiple_documents()

	def reconcile_multiple_transactions_with_one_document(self):
		reconciled_amount = 0
		for bank_transaction in self.bank_transactions:
			if abs(self.documents[0]["unreconciled_amount"]) > reconciled_amount:
				bank_transaction = frappe.get_doc("Bank Transaction", bank_transaction.get("name"))
				allocated_amount = min(
					max(abs(bank_transaction.unallocated_amount), 0),
					abs(self.documents[0]["unreconciled_amount"]),
				)
				date_value = self.documents[0].get("reference_date")
				if isinstance(date_value, str):
					date_value = parse_date(date_value)

				if allocated_amount > 0:
					bank_transaction.append(
						"payment_entries",
						{
							"payment_document": self.reconciliation_doctype,
							"payment_entry": self.documents[0]["name"],
							"allocated_amount": allocated_amount,
							"party": self.documents[0][PARTY_FIELD.get(self.reconciliation_doctype)],
							"date": getdate(date_value),
						},
					)

					reconciled_amount += allocated_amount
					bank_transaction.save()

	def reconcile_one_transaction_with_multiple_documents(self):
		for document in self.documents:
			bank_transaction = frappe.get_doc("Bank Transaction", self.bank_transactions[0]["name"])
			date_value = document.get("reference_date") or document.get("date")
			if isinstance(date_value, str):
				date_value = parse_date(date_value)

			if flt(bank_transaction.unallocated_amount) != 0:
				bank_transaction.append(
					"payment_entries",
					{
						"payment_document": document.get("doctype"),
						"payment_entry": document.get("name"),
						"allocated_amount": abs(document.get("unreconciled_amount")),
						"party": document.get(PARTY_FIELD.get(document.get("doctype"))),
						"date": getdate(date_value),
					},
				)

				bank_transaction.save()

	def reconcile_created_payments(self):
		for transaction, payment in zip(self.bank_transactions, self.payment_entries):
			bank_transaction = frappe.get_doc("Bank Transaction", transaction.get("name"))
			date_value = payment.get("reference_date")
			if isinstance(date_value, str):
				date_value = parse_date(date_value)

			bank_transaction.append(
				"payment_entries",
				{
					"payment_document": payment.get("doctype"),
					"payment_entry": payment.get("name"),
					"allocated_amount": min(
						abs(payment.get("unreconciled_amount")), abs(bank_transaction.unallocated_amount)
					),
					"party": payment.get(PARTY_FIELD.get(payment.get("doctype"))),
					"date": getdate(date_value),
				},
			)

			bank_transaction.save()

	def make_payment_entries(self):
		if self.documents:
			for transaction in self.bank_transactions:
				payment_entry = self.get_payment_entry(transaction)
				payment_entry.insert()
				payment_entry.submit()
				frappe.db.commit()
				self.payment_entries.append(payment_entry)

	def get_payment_entry(self, transaction):
		party_account_currency = get_account_currency(self.party_account)

		# payment type
		if (self.reconciliation_doctype == "Sales Invoice" and transaction.get("amount") > 0) or (
			self.reconciliation_doctype == "Purchase Invoice" and transaction.get("amount") > 0
		):
			payment_type = "Receive"
		else:
			payment_type = "Pay"

		# total outstanding
		total_outstanding_amount = 0
		if self.reconciliation_doctype in ("Sales Invoice", "Purchase Invoice"):
			total_outstanding_amount = sum([x.get("outstanding_amount") for x in self.documents])
		elif self.reconciliation_doctype in ("Expense Claim"):
			total_outstanding_amount = sum(
				[(flt(x.get("grand_total")) - flt(x.get("total_amount_reimbursed"))) for x in self.documents]
			)
		elif self.reconciliation_doctype == "Employee Advance":
			total_outstanding_amount = sum(
				[(flt(x.get("advance_amount")) - flt(x.get("paid_amount"))) for x in self.documents]
			)

		bank_account = frappe.get_doc("Bank Account", transaction.get("bank_account"))
		account_currency = frappe.db.get_value("Account", bank_account.account, "account_currency")

		paid_amount = received_amount = 0
		amount_to_pay_or_receive = (
			abs(transaction.get("unallocated_amount"))
			if abs(transaction.get("unallocated_amount")) <= total_outstanding_amount
			else total_outstanding_amount
		)
		if party_account_currency == account_currency:
			paid_amount = received_amount = amount_to_pay_or_receive
		elif payment_type == "Receive":
			paid_amount = amount_to_pay_or_receive
			received_amount = total_outstanding_amount
		else:
			received_amount = amount_to_pay_or_receive
			paid_amount = total_outstanding_amount

		pe = frappe.new_doc("Payment Entry")
		pe.payment_type = payment_type
		pe.company = bank_account.company
		pe.cost_center = self.cost_center
		pe.posting_date = getdate(parse_date(transaction.get("date")))
		pe.mode_of_payment = self.mode_of_payment
		pe.party_type = self.party_type
		pe.party = self.party
		contacts = [x.get("contact_person") for x in self.documents]
		pe.contact_person = contacts[0] if contacts else None
		pe.contact_email = " ,".join(
			list(set([x.get("contact_email") for x in self.documents if x.get("contact_email")]))
		)[:140]
		pe.ensure_supplier_is_not_blocked()

		pe.paid_from = self.party_account if payment_type == "Receive" else bank_account.account
		pe.paid_to = self.party_account if payment_type == "Pay" else bank_account.account
		pe.paid_from_account_currency = (
			party_account_currency if payment_type == "Receive" else account_currency
		)
		pe.paid_to_account_currency = (
			party_account_currency if payment_type == "Pay" else account_currency
		)
		pe.paid_amount = paid_amount
		pe.received_amount = received_amount
		letter_heads = [x.get("letter_head") for x in self.documents]
		pe.letter_head = letter_heads[0] if letter_heads else None
		pe.reference_no = transaction.get("reference_number") or transaction.get("name")
		pe.reference_date = getdate(parse_date(transaction.get("date")))
		pe.bank_account = bank_account.name

		if pe.party_type in ["Customer", "Supplier"]:
			bank_account = get_party_bank_account(pe.party_type, pe.party)
			pe.set("party_bank_account", bank_account)
		pe.set_bank_account_data()

		total_allocated_amount = 0
		for doc in self.documents:
			# only Purchase Invoice can be blocked individually
			if doc.get("doctype") == "Purchase Invoice":
				pi = frappe.get_doc("Purchase Invoice", doc.get("name"))
				if pi.invoice_is_blocked():
					frappe.throw(_("{0} is on hold till {1}".format(pi.name, pi.release_date)))

			# amounts
			grand_total = outstanding_amount = 0
			if self.reconciliation_doctype in ("Sales Invoice", "Purchase Invoice"):
				if party_account_currency == doc.get("company_currency"):
					grand_total = doc.get("base_rounded_total") or doc.get("base_grand_total")
				else:
					grand_total = doc.get("rounded_total") or doc.get("grand_total")
				outstanding_amount = doc.get("outstanding_amount")
			elif self.reconciliation_doctype in ("Expense Claim"):
				grand_total = doc.get("total_sanctioned_amount") + doc.get("total_taxes_and_charges")
				outstanding_amount = doc.get("grand_total") - doc.get("total_amount_reimbursed")
			elif self.reconciliation_doctype == "Employee Advance":
				grand_total = doc.get("advance_amount")
				outstanding_amount = flt(doc.get("advance_amount")) - flt(doc.get("paid_amount"))
			else:
				if party_account_currency == doc.get("company_currency"):
					grand_total = flt(doc.get("base_rounded_total") or doc.get("base_grand_total"))
				else:
					grand_total = flt(doc.get("rounded_total") or doc.get("grand_total"))
				outstanding_amount = grand_total - flt(doc.get("advance_paid"))

			allocated_amount = min(
				outstanding_amount,
				flt(abs(transaction.get("unallocated_amount"))) - flt(total_allocated_amount),
			)

			pe.append(
				"references",
				{
					"reference_doctype": doc.get("doctype"),
					"reference_name": doc.get("name"),
					"bill_no": doc.get("bill_no"),
					"due_date": doc.get("due_date"),
					"total_amount": grand_total,
					"outstanding_amount": outstanding_amount,
					"allocated_amount": allocated_amount,
				},
			)

			total_allocated_amount += allocated_amount

		pe.setup_party_account_field()
		pe.set_missing_values()
		if self.party_account and bank_account:
			pe.set_exchange_rate()
			pe.set_amounts()
		return pe
