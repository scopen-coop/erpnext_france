# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from erpnext.accounts.utils import update_voucher_outstanding

#
# Outstanding amount of Sales Invoice was autoupdated when Payment Ledger Entry was updated
# But the right value could only be calculated from Sales Invoice.
#
def on_update(doc, method):
	if doc.voucher_type != 'Sales Invoice':
		return

	si = frappe.get_doc('Sales Invoice', doc.voucher_no)
	if si.total_advance > 0 and doc.amount_in_account_currency > 0 and si.grand_total == doc.amount_in_account_currency:
		doc.amount_in_account_currency = si.grand_total - si.total_advance
		frappe.db.set_value(
			doc.voucher_type,
			doc.voucher_no,
			"outstanding_amount",
			doc.amount_in_account_currency,
		)
