# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt
import frappe
from erpnext import is_perpetual_inventory_enabled
from erpnext.accounts.doctype.pricing_rule.utils import update_coupon_code_count
from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
	SalesInvoice,
	update_linked_doc,
)
from erpnext.accounts.doctype.tax_withholding_entry.tax_withholding_entry import SalesTaxWithholding
from erpnext.accounts.general_ledger import merge_similar_entries
from erpnext.accounts.party import get_party_account
from erpnext.accounts.utils import get_account_currency
from erpnext.controllers.accounts_controller import validate_account_head
from erpnext.setup.doctype.company.company import update_company_current_month_sales
from frappe import _
from frappe.utils import cint, flt

from erpnext_france.controllers.accounts_controller import (
	update_against_document_in_jv,
)


class SalesInvoiceFrance(SalesInvoice):
	def on_submit(self):
		self.validate_pos_paid_amount()

		if not self.auto_repeat:
			frappe.get_cached_doc("Authorization Control").validate_approving_authority(
				self.doctype, self.company, self.base_grand_total, self
			)

		self.check_prev_docstatus()

		if self.is_return and not self.update_billed_amount_in_sales_order:
			# NOTE status updating bypassed for is_return
			self.status_updater = []

		SalesTaxWithholding(self).on_submit()

		self.update_status_updater_args()
		self.update_prevdoc_status()

		self.update_billing_status_in_dn()
		self.clear_unallocated_mode_of_payments()

		# Updating stock ledger should always be called after updating prevdoc status,
		# because updating reserved qty in bin depends upon updated delivered qty in SO
		if self.update_stock == 1:
			for table_name in ["items", "packed_items"]:
				if not self.get(table_name):
					continue

				self.make_bundle_for_sales_purchase_return(table_name)
				self.make_bundle_using_old_serial_batch_fields(table_name)

			self.validate_standalone_serial_nos_customer()
			self.update_stock_reservation_entries()
			self.update_stock_ledger()

		self.split_asset_based_on_sale_qty()

		self.process_asset_depreciation()

		# this sequence because outstanding may get -ve
		self.make_gl_entries()

		if self.update_stock == 1:
			self.repost_future_sle_and_gle()
			self.update_pick_list_status()

		if not self.is_return:
			self.update_billing_status_for_zero_amount_refdoc("Delivery Note")
			self.update_billing_status_for_zero_amount_refdoc("Sales Order")
			self.check_credit_limit()

		if cint(self.is_pos) != 1 and not self.is_return:
			update_against_document_in_jv(self)  # Erpnext France Modif

		self.update_time_sheet(None if (self.is_return and self.return_against) else self.name)

		if frappe.get_single_value("Selling Settings", "sales_update_frequency") == "Each Transaction":
			update_company_current_month_sales(self.company)
			self.update_project()
		update_linked_doc(self.doctype, self.name, self.inter_company_invoice_reference)

		if self.coupon_code:
			update_coupon_code_count(self.coupon_code, "used")

		# create the loyalty point ledger entry if the customer is enrolled in any loyalty program
		if (
			not self.is_return
			and not self.is_consolidated
			and self.loyalty_program
			and not self.dont_create_loyalty_points
		):
			self.make_loyalty_point_entry()
		elif self.is_return and self.return_against and not self.is_consolidated and self.loyalty_program:
			against_si_doc = frappe.get_doc("Sales Invoice", self.return_against)
			against_si_doc.delete_loyalty_point_entry()
			against_si_doc.make_loyalty_point_entry()
		if self.redeem_loyalty_points and not self.is_consolidated and self.loyalty_points:
			self.apply_loyalty_points()

		self.process_common_party_accounting()
		self.update_billed_qty_in_scio()

	def _validate(self):
		super()._validate()

	def set_payment_schedule(self):
		import erpnext.controllers.accounts_controller as ac

		from erpnext_france.controllers.party import get_payment_term_details as our_get_payment_term_details

		original = ac.get_payment_term_details
		ac.get_payment_term_details = our_get_payment_term_details
		try:
			super().set_payment_schedule()
		finally:
			ac.get_payment_term_details = original

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

	def get_gl_entries(self, inventory_account_map=None):
		gl_entries = []

		self.make_customer_gl_entry(gl_entries)

		self.make_tax_gl_entries(gl_entries)
		self.make_internal_transfer_gl_entries(gl_entries)

		self.make_item_gl_entries(gl_entries)
		self.make_precision_loss_gl_entry(gl_entries)
		self.make_discount_gl_entries(gl_entries)

		self.make_down_payment_final_invoice_entries(gl_entries)

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
			frappe.db.get_single_value("Selling Settings", "enable_discount_accounting")
		)

		for item in self.get("items"):
			if (
				flt(item.base_net_amount, item.precision("base_net_amount"))
				or item.is_fixed_asset
				or enable_discount_accounting
			):
				# Do not book income for transfer within same company
				if self.is_internal_transfer():
					continue

				if item.is_fixed_asset and item.asset:
					self.get_gl_entries_for_fixed_asset(item, gl_entries)
				else:
					income_account = (
						item.income_account
						if (
							not item.enable_deferred_revenue or self.is_return or self.is_down_payment_invoice
						)
						else item.deferred_revenue_account
					)
					amount, base_amount = self.get_amount_and_base_amount(item, enable_discount_accounting)

					account_currency = get_account_currency(income_account)
					gl_dict = self.get_gl_dict(
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
							"remarks": item.get("remarks")
							or f'{_("Item")}: {item.qty} {item.item_code} - {_(item.uom)} / {_("Customer")}: {self.customer}',
							"accounting_journal": self.accounting_journal,
						},
						account_currency,
						item=item,
					)

					gl_entries.append(gl_dict)

		# expense account gl entries
		if cint(self.update_stock) and is_perpetual_inventory_enabled(self.company):
			gl_entries += super(SalesInvoice, self).get_gl_entries()

	def get_gl_entries_for_fixed_asset(self, item, gl_entries):
		# Délègue à la méthode v16, puis injecte accounting_journal sur les entrées ajoutées
		before = len(gl_entries)
		super().get_gl_entries_for_fixed_asset(item, gl_entries)
		for gle in gl_entries[before:]:
			gle["accounting_journal"] = self.accounting_journal

	def validate_due_date(self):
		if self.get("is_pos"):
			return
		from frappe.utils import getdate

		from erpnext_france.controllers.party import validate_due_date as validate_due_date_france

		posting_date = self.posting_date
		if frappe.flags.in_import and getdate(self.due_date) < getdate(posting_date):
			self.due_date = posting_date
		elif self.doctype == "Sales Invoice":
			if not self.due_date:
				frappe.throw(_("Due Date is mandatory"))
			validate_due_date_france(
				posting_date, self.due_date, None, self.payment_terms_template, self.doctype
			)

	def validate_invoice_documents_schedule(self):
		if (
			self.is_return
			or (self.doctype == "Purchase Invoice" and self.is_paid)
			or (self.doctype == "Sales Invoice" and self.is_pos)
			or self.get("is_opening") == "Yes"
		):
			self.payment_terms_template = ""
			self.payment_schedule = []
		if self.is_return:
			return
		self.validate_payment_schedule_dates()
		self.set_payment_schedule()

		self.set_due_date()
		if not self.get("ignore_default_payment_terms_template"):
			self.validate_payment_schedule_amount()
			self.validate_due_date()
		self.validate_advance_entries()
