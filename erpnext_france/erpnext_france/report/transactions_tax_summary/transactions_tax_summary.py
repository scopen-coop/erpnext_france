# Copyright (c) 2021, Dokos SAS and contributors
# For license information, please see license.txt

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import flt, rounded

from erpnext.controllers.taxes_and_totals import get_itemised_tax


def execute(filters=None):
	return get_data(filters)


def get_data(filters=None):
	summary = TaxSummary(filters)
	return summary.get_data()


class TaxSummary:
	def __init__(self, filters):
		self.filters = filters
		self.data = []
		self.columns = []
		self.tax_rates = []
		self.tax_accounts = frappe.get_all(
			"Account", filters={"is_group": 0, "account_type": "Tax"}, pluck="name"
		)
		self.parents = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

	def get_data(self):
		if not self.filters.transaction_type or self.filters.transaction_type == "Sales Invoice":
			self.get_data_from_sales_invoices()
		if self.filters.transaction_type == "Purchase Invoice":
			self.get_data_from_purchase_invoices()

		self.calculate_totals()
		self.get_columns()

		return self.columns, self.data

	def get_data_from_sales_invoices(self):
		self.transaction = "Sales Invoice"
		self.get_data_from_transactions()

	def get_data_from_purchase_invoices(self):
		self.transaction = "Purchase Invoice"
		self.get_data_from_transactions()

	def get_data_from_transactions(self):
		transactions_headers = {
			x.name: (x.posting_date, x.base_grand_total)
			for x in frappe.get_all(
				self.transaction,
				filters={
					"company": self.filters.company,
					"posting_date": ("between", (self.filters.period_start_date, self.filters.period_end_date)),
					"docstatus": 1,
				},
				fields=["name", "posting_date", "base_grand_total"],
				order_by="posting_date desc, name desc",
			)
		}

		for document in transactions_headers.keys():
			if document not in self.parents.get(self.transaction, {}).keys():
				self.data.append(
					{
						"date": transactions_headers.get(document)[0],
						"indent": 0,
						"reference_doctype": self.transaction,
						"reference_document": document,
						"base_grand_total": transactions_headers.get(document)[1],
					}
				)

			doc = frappe.get_cached_doc(self.transaction, document)
			itemised_tax = get_itemised_tax(doc.taxes, True)

			processed_items = []
			for item in doc.items:
				base_net_amount = item.base_net_amount
				self.parents[self.transaction][item.parent]["base_net_amount"] += flt(base_net_amount)

				if item.item_code in processed_items:
					for data in reversed(self.data):
						if data.get("item_code") == item.item_code:
							data["base_net_amount"] += flt(base_net_amount)
					continue
				else:
					processed_items.append(item.item_code)

				row = {
					"indent": 1,
					"item_code": item.item_code,
					"base_net_amount": flt(base_net_amount),
				}

				total_amount = 0
				if itemised_tax:
					for tax in itemised_tax.get(item.item_code):
						if itemised_tax[item.item_code][tax].get("tax_account") not in self.tax_accounts:
							tax_rate = -99.0
						else:
							tax_rate = flt(itemised_tax[item.item_code][tax].get("tax_rate")) * flt(
								-1.0 if itemised_tax[item.item_code][tax].get("add_deduct_tax") == "Deduct" else 1.0
							)

						if tax_rate not in self.tax_rates:
							self.tax_rates.append(tax_rate)

						tax_amount = flt(itemised_tax[item.item_code][tax].get("tax_amount")) * flt(
							-1.0 if itemised_tax[item.item_code][tax].get("add_deduct_tax") == "Deduct" else 1.0
						)
						row.update({tax_rate: tax_amount})
						self.parents[self.transaction][item.parent][tax_rate] += tax_amount

				self.data.append(row)

	def calculate_totals(self):
		total_row = frappe._dict(
			{
				"item_code": _("Total"),
				"indent": 0,
				"base_net_amount": 0.0,
				"base_grand_total": 0.0,
				"difference": 0.0,
			}
		)

		for rate in self.tax_rates:
			total_row.update({rate: 0.0})

		for data in self.data:
			if data.get("indent") == 0:
				base_net_amount = flt(
					self.parents.get(data.get("reference_doctype"), {})
					.get(data.get("reference_document"), {})
					.get("base_net_amount")
				)
				data.update({"base_net_amount": base_net_amount})
				total_row["base_net_amount"] += base_net_amount

				total_row["base_grand_total"] += data.get("base_grand_total")

				difference = flt(data.get("base_grand_total")) - flt(base_net_amount)

				for tax in self.parents.get(data.get("reference_doctype"), {}).get(
					data.get("reference_document"), {}
				):
					if tax not in ("base_net_amount", "base_grand_amount"):
						tax_amount = flt(
							self.parents.get(data.get("reference_doctype"), {})
							.get(data.get("reference_document"), {})
							.get(tax)
						)
						data.update({tax: tax_amount})
						total_row[tax] += tax_amount
						difference -= tax_amount

				data.update({"difference": rounded(difference, precision=2)})
				total_row["difference"] += difference

		total_row["difference"] = rounded(total_row["difference"], precision=2)
		self.data.extend([{}, total_row])

	def get_columns(self):
		self.columns = [
			{"fieldname": "date", "label": _("Reference Date"), "fieldtype": "Date", "width": 120},
			{
				"fieldname": "reference_doctype",
				"label": _("Reference DocType"),
				"fieldtype": "Link",
				"options": "DocType",
				"width": 180,
			},
			{
				"fieldname": "reference_document",
				"label": _("Reference Document"),
				"fieldtype": "Dynamic Link",
				"options": "reference_doctype",
				"width": 180,
			},
			{
				"fieldname": "item_code",
				"label": _("Item Code"),
				"fieldtype": "Link",
				"options": "Item",
				"width": 180,
			},
			{
				"fieldname": "base_grand_total",
				"label": _("Base Grand Total"),
				"fieldtype": "Currency",
				"width": 180,
			},
			{
				"fieldname": "base_net_amount",
				"label": _("Base Net Amount"),
				"fieldtype": "Currency",
				"width": 180,
			},
		]

		self.tax_rates.sort(reverse=True)
		for rate in self.tax_rates:
			self.columns.append(
				{
					"fieldname": str(rate),
					"label": f"{str(rate)} %" if rate != -99.0 else _("Other charges"),
					"fieldtype": "Currency",
					"width": 180,
				}
			)
