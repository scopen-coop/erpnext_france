# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt
import frappe
from erpnext import is_perpetual_inventory_enabled
from erpnext.accounts.doctype.gl_entry.gl_entry import rename_temporarily_named_docs
from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
	SalesInvoice,
	update_linked_doc,
)
from erpnext.accounts.general_ledger import merge_similar_entries
from erpnext.accounts.party import get_party_account
from erpnext.accounts.utils import get_account_currency
from erpnext.assets.doctype.asset.depreciation import (
	depreciate_asset,
	get_gl_entries_on_asset_disposal,
	get_gl_entries_on_asset_regain,
	reset_depreciation_schedule,
)
from erpnext.controllers.accounts_controller import validate_account_head
from erpnext.setup.doctype.company.company import update_company_current_month_sales
from frappe import _
from frappe.utils import cint, flt

from erpnext_france.controllers.accounts_controller import (
	make_exchange_gain_loss_gl_entries,
	update_against_document_in_jv,
)


class SalesInvoiceDownPayment(SalesInvoice):
	def validate(self):
		super().validate()

		if (
			cint(self.is_down_payment_invoice)
			and len(list(set([x.sales_order for x in self.get("items")]))) > 1
		):
			frappe.throw(_("Down payment invoices can only be made against a single sales order."))

		self.validate_down_payment_advances()

		for item in self.get("items"):
			validate_account_head(
				item.idx,
				item.income_account,
				self.company,
				_("Income", context="Account Validation"),
			)

	def validate_down_payment_advances(self):
		for advance in self.get("advances"):
			if (
				flt(advance.allocated_amount) <= flt(advance.advance_amount)
				and advance.reference_type == "Payment Entry"
				and cint(advance.is_down_payment)
			):
				advance.allocated_amount = advance.advance_amount

	def make_down_payment_final_invoice_entries(self, gl_entries):
		# In the case of a down payment with multiple payments, associated entries of
		# the gl_entries list would be credited/debited multiple times if we didn't make
		# sure that the pair of GL Entry was not already processed.
		handled_down_payment_entries: set[str] = set()

		for d in self.get("advances"):
			if (
				flt(d.allocated_amount) <= 0
				or d.reference_type != "Payment Entry"
				or not cint(d.is_down_payment)
			):
				continue

			payment_entry = frappe.get_doc(d.reference_type, d.reference_name)
			down_payment_entries = []
			gl_entry = frappe.qb.DocType("GL Entry")

			for ref in payment_entry.references:
				down_payment_entries.extend(
					(
						frappe.qb.from_(gl_entry)
						.select(
							"name",
							"account",
							"against",
							"debit",
							"debit_in_account_currency",
							"credit",
							"credit_in_account_currency",
						)
						.where(gl_entry.voucher_type == ref.reference_doctype)
						.where(gl_entry.voucher_no == ref.reference_name)
						.where(gl_entry.is_cancelled == 0)
						.for_update()
					).run(as_dict=1)
				)

			down_payment_accounts = [
				entry["against"] for entry in down_payment_entries if entry["account"] == self.debit_to
			]

			for down_payment_entry in down_payment_entries:
				if down_payment_entry["account"] in down_payment_accounts and not [
					x for x in gl_entries if x["account"] == down_payment_entry["account"]
				]:
					gl_entries.append(
						self.get_gl_dict(
							{
								"account": down_payment_entry["account"],
								"against": down_payment_entry["account"],
								"party_type": "Customer",
								"party": self.customer,
								"accounting_journal": self.accounting_journal,
							},
							self.currency,
						)
					)

			for down_payment_entry in down_payment_entries:
				if down_payment_entry["name"] in handled_down_payment_entries:
					# Skip this down payment entry if it has already been handled,
					# possibly for a previous payment entry.
					continue

				handled_down_payment_entries.add(down_payment_entry["name"])

				for gl_entry in gl_entries:
					if gl_entry["account"] != down_payment_entry["account"]:
						continue
					if gl_entry["account"] not in down_payment_accounts:
						gl_entry["debit"] -= down_payment_entry["debit"]
						gl_entry["debit_in_account_currency"] -= down_payment_entry[
							"debit_in_account_currency"
						]
						gl_entry["credit"] -= down_payment_entry["credit"]
						gl_entry["credit_in_account_currency"] -= down_payment_entry[
							"credit_in_account_currency"
						]
					else:
						gl_entry["debit"] += down_payment_entry["credit"]
						gl_entry["debit_in_account_currency"] += down_payment_entry[
							"credit_in_account_currency"
						]

	def get_gl_entries(self, warehouse_account=None):
		gl_entries = []

		self.make_customer_gl_entry(gl_entries)

		self.make_tax_gl_entries(gl_entries)
		self.make_internal_transfer_gl_entries(gl_entries)

		self.make_item_gl_entries(gl_entries)
		self.make_precision_loss_gl_entry(gl_entries)
		self.make_discount_gl_entries(gl_entries)

		# ERPNEXT_FRANCE
		self.make_down_payment_final_invoice_entries(gl_entries)
		# END ERPNEXT_FRANCE

		# merge gl entries before adding pos entries
		gl_entries = merge_similar_entries(gl_entries)

		self.make_loyalty_point_redemption_gle(gl_entries)
		self.make_pos_gl_entries(gl_entries)

		self.make_write_off_gl_entry(gl_entries)
		self.make_gle_for_rounding_adjustment(gl_entries)

		self.set_transaction_currency_and_rate_in_gl_map(gl_entries)
		return gl_entries

	def make_item_gl_entries(self, gl_entries):
		# income account gl entries
		enable_discount_accounting = cint(
			frappe.get_single_value("Selling Settings", "enable_discount_accounting")
		)

		for item in self.get("items"):
			if flt(item.base_net_amount, item.precision("base_net_amount")) or item.is_fixed_asset:
				# Do not book income for transfer within same company
				if self.is_internal_transfer():
					continue

				if item.is_fixed_asset and item.asset:
					self.get_gl_entries_for_fixed_asset(item, gl_entries)
				else:
					# ERPNEXT France
					income_account = (
						item.income_account
						if (not item.enable_deferred_revenue or self.is_return or self.is_down_payment_invoice) # ERPNEXT France
						else item.deferred_revenue_account
					)
					# END ERPNEXT France

					amount, base_amount = self.get_amount_and_base_amount(item, enable_discount_accounting)

					account_currency = get_account_currency(income_account)
					gl_entries.append(
						self.get_gl_dict(
							{
								"account": income_account,
								"against": self.customer,
								"credit": flt(base_amount, item.precision("base_net_amount")),
								"credit_in_account_currency": (
									flt(base_amount, item.precision("base_net_amount"))
									if account_currency == self.company_currency
									else flt(amount, item.precision("net_amount"))
								),
								"credit_in_transaction_currency": flt(amount, item.precision("net_amount")),
								"cost_center": item.cost_center,
								"project": item.project or self.project,
							},
							account_currency,
							item=item,
						)
					)

		# expense account gl entries
		if cint(self.update_stock) and is_perpetual_inventory_enabled(self.company):
			gl_entries += super().get_gl_entries()