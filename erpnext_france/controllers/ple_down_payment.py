import frappe
from frappe import _
from erpnext.accounts.utils import update_voucher_outstanding


def on_update(doc, method):
#	payment_ledger_entries = frappe.get_list('Payment Ledger Entry',
#		filters={
#			"voucher_type": 'Sales Invoice',
#			"voucher_no": doc.name,
#		}
#	)
	if doc.voucher_type == 'Sales Invoice':
		si = frappe.get_doc('Sales Invoice', doc.voucher_no)
		if si.total_advance > 0 and si.grand_total == doc.amount_in_account_currency:
			doc.amount_in_account_currency = sign(doc.amount_in_account_currency) * (si.grand_total - si.total_advance)
			frappe.db.set_value(
				doc.voucher_type,
				doc.voucher_no,
				"outstanding_amount",
				doc.amount_in_account_currency,
			)


def sign(value):
	if value > 0: return 1
	if value < 0: return - 1
	else: return 0