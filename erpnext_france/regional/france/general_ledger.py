# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

import copy

import frappe
from frappe import _
from frappe.model.meta import get_field_precision
from frappe.model.naming import make_autoname
from frappe.utils import cint, cstr, flt, formatdate, getdate, now

import erpnext
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from erpnext.accounts.doctype.budget.budget import validate_expense_against_budget
from erpnext.accounts.utils import create_payment_ledger_entry
from erpnext.accounts.general_ledger import (
	make_entry,
	check_freezing_date,
	validate_against_pcv,
	set_as_cancel,
	process_debit_credit_difference,
	validate_cwip_accounts,
	toggle_debit_credit_if_negative,
	distribute_gl_based_on_cost_center_allocation,
	validate_accounting_period,
	validate_disabled_accounts,
	make_acc_dimensions_offsetting_entry,
	check_if_in_list
)


def make_gl_entries(
	gl_map,
	cancel=False,
	adv_adj=False,
	merge_entries=True,
	update_outstanding="Yes",
	from_repost=False,
):
	if gl_map:
		if not cancel:
			make_acc_dimensions_offsetting_entry(gl_map)
			validate_accounting_period(gl_map)
			validate_disabled_accounts(gl_map)
			gl_map = process_gl_map(gl_map, merge_entries)
			if gl_map and len(gl_map) > 1:
				create_payment_ledger_entry(
					gl_map,
					cancel=0,
					adv_adj=adv_adj,
					update_outstanding=update_outstanding,
					from_repost=from_repost,
				)
				save_entries(gl_map, adv_adj, update_outstanding, from_repost)
			# Post GL Map proccess there may no be any GL Entries
			elif gl_map:
				frappe.throw(
					_(
						"Incorrect number of General Ledger Entries found. You might have selected a wrong Account in the transaction."
					)
				)
		else:
			make_reverse_gl_entries(gl_map, adv_adj=adv_adj, update_outstanding=update_outstanding)

def process_gl_map(gl_map, merge_entries=True, precision=None):
	if not gl_map:
		return []

	if gl_map[0].voucher_type != "Period Closing Voucher":
		gl_map = distribute_gl_based_on_cost_center_allocation(gl_map, precision)

	if merge_entries:
		gl_map = merge_similar_entries(gl_map, precision)

	gl_map = toggle_debit_credit_if_negative(gl_map)

	return gl_map

def merge_similar_entries(gl_map, precision=None):
	merged_gl_map = []
	accounting_dimensions = get_accounting_dimensions()

	for entry in gl_map:
		# if there is already an entry in this account then just add it
		# to that entry
		same_head = check_if_in_list(entry, merged_gl_map, accounting_dimensions)
		if same_head:
			same_head.debit = flt(same_head.debit) + flt(entry.debit)
			same_head.debit_in_account_currency = flt(same_head.debit_in_account_currency) + flt(
				entry.debit_in_account_currency
			)
			same_head.credit = flt(same_head.credit) + flt(entry.credit)
			same_head.credit_in_account_currency = flt(same_head.credit_in_account_currency) + flt(
				entry.credit_in_account_currency
			)
			if not same_head.remarks:
				same_head.remarks = entry.remarks
			else:
				same_head.remarks += f"\n{entry.remarks}"
		else:
			merged_gl_map.append(entry)

	company = gl_map[0].company if gl_map else erpnext.get_default_company()
	company_currency = erpnext.get_company_currency(company)

	if not precision:
		precision = get_field_precision(frappe.get_meta("GL Entry").get_field("debit"), company_currency)

	# filter zero debit and credit entries
	merged_gl_map = filter(
		lambda x: flt(x.debit, precision) != 0
		or flt(x.credit, precision) != 0
		or (
			x.voucher_type == "Journal Entry"
			and frappe.get_cached_value("Journal Entry", x.voucher_no, "voucher_type")
			== "Exchange Gain Or Loss"
		),
		merged_gl_map,
	)
	merged_gl_map = list(merged_gl_map)

	return merged_gl_map

def save_entries(gl_map, adv_adj, update_outstanding, from_repost=False):
	if not from_repost:
		validate_cwip_accounts(gl_map)

	process_debit_credit_difference(gl_map)

	if gl_map:
		check_freezing_date(gl_map[0]["posting_date"], adv_adj)
		is_opening = any(d.get("is_opening") == "Yes" for d in gl_map)
		if gl_map[0]["voucher_type"] != "Period Closing Voucher":
			validate_against_pcv(is_opening, gl_map[0]["posting_date"], gl_map[0]["company"])

	accounting_number = get_accounting_number(gl_map[0])
	for entry in gl_map:
		entry["accounting_entry_number"] = accounting_number
		if not entry.get("accounting_journal"):
			get_accounting_journal(entry)

		make_entry(entry, adv_adj, update_outstanding, from_repost)


def get_accounting_number(doc: dict) -> str:
	return make_autoname(_("AEN-.fiscal_year.-.#########"), "GL Entry", doc)

def get_accounting_journal(entry):
	rules = frappe.get_all(
		"Accounting Journal",
		filters={"company": entry.get("company"), "disabled": 0},
		fields=[
			"name",
			"type",
			"account",
			"`tabAccounting Journal Rule`.document_type",
			"`tabAccounting Journal Rule`.condition",
		],
	)

	applicable_rules = [
		rule for rule in rules if (rule.account in (entry.account, entry.against, None))
	]
	if applicable_rules:
		applicable_rules = sorted(
			[rule for rule in applicable_rules if rule.document_type in (entry.voucher_type, None)],
			key=lambda r: r.get("document_type") or "",
			reverse=True,
		)
	else:
		applicable_rules = [rule for rule in rules if rule.document_type == entry.voucher_type]

	for condition in [rule for rule in applicable_rules if rule.condition]:
		if frappe.safe_eval(
			condition.condition,
			None,
			{"doc": frappe.get_doc(entry.get("voucher_type"), entry.get("voucher_no")).as_dict()},
		):
			entry["accounting_journal"] = condition.name
			break

	if not entry.get("accounting_journal") and [
		rule for rule in applicable_rules if not rule.condition
	]:
		entry["accounting_journal"] = [rule for rule in applicable_rules if not rule.condition][0].name

	if not entry.get("accounting_journal"):
		entry["accounting_journal"] = frappe.db.get_value(
			"GL Entry",
			dict(accounting_entry_number=entry.get("accounting_entry_number")),
			"accounting_journal",
		)

	if not entry.get("accounting_journal") and cint(
		frappe.db.get_single_value("Accounts Settings", "mandatory_accounting_journal")
	):
		frappe.throw(
			_(
				"Please configure an accounting journal for this transaction type and account: {0} - {1}"
			).format(_(entry.voucher_type), entry.get("account"))
		)

def make_reverse_gl_entries(
	gl_entries=None,
	voucher_type=None,
	voucher_no=None,
	adv_adj=False,
	update_outstanding="Yes",
	cancel_payment_ledger_entries=True,  # @dokos
):
	"""
	Get original gl entries of the voucher
	and make reverse gl entries by swapping debit and credit
	"""

	if not gl_entries:
		gl_entry = frappe.qb.DocType("GL Entry")
		gl_entries = (
			frappe.qb.from_(gl_entry)
			.select("*")
			.where(gl_entry.voucher_type == voucher_type)
			.where(gl_entry.voucher_no == voucher_no)
			.where(gl_entry.is_cancelled == 0)
			.for_update()
		).run(as_dict=1)

	if gl_entries:
		if cancel_payment_ledger_entries:  # @dokos
			create_payment_ledger_entry(
				gl_entries,
				cancel=1,
				adv_adj=adv_adj,
				update_outstanding=update_outstanding
			)
		validate_accounting_period(gl_entries)
		check_freezing_date(gl_entries[0]["posting_date"], adv_adj)
		set_as_cancel(gl_entries[0]["voucher_type"], gl_entries[0]["voucher_no"])

		accounting_number = get_accounting_number(gl_entries[0])
		for entry in gl_entries:
			new_gle = copy.deepcopy(entry)
			new_gle["name"] = None
			new_gle["accounting_entry_number"] = accounting_number
			debit = new_gle.get("debit", 0)
			credit = new_gle.get("credit", 0)

			debit_in_account_currency = new_gle.get("debit_in_account_currency", 0)
			credit_in_account_currency = new_gle.get("credit_in_account_currency", 0)

			new_gle["debit"] = credit
			new_gle["credit"] = debit
			new_gle["debit_in_account_currency"] = credit_in_account_currency
			new_gle["credit_in_account_currency"] = debit_in_account_currency

			if not new_gle["remarks"]:
				new_gle["remarks"] = _("On cancellation of ") + new_gle["voucher_no"]

			new_gle["is_cancelled"] = 1

			if not new_gle.get("accounting_journal"):
				get_accounting_journal(new_gle)

			if new_gle["debit"] or new_gle["credit"]:
				make_entry(new_gle, adv_adj, "Yes")
