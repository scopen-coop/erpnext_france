import frappe
from frappe import _
from frappe.utils import cint, flt

from erpnext.controllers.accounts_controller import AccountsController
from erpnext.controllers.accounts_controller import (
    get_advance_payment_entries_for_regional,
    get_advance_journal_entrie,
    get_advance_payment_entries
)

from erpnext.accounts.party import get_party_account


@frappe.whitelist()
def set_advances(doc):
    """Returns list of advances against Account, Party, Reference"""

    res = doc.get_advance_entries(
        include_unallocated=not cint(doc.get("only_include_allocated_payments"))
    )

    doc.set("advances", [])
    advance_allocated = 0
    for d in res:
        if doc.get("party_account_currency") == doc.company_currency:
            amount = doc.get("base_rounded_total") or doc.base_grand_total
        else:
            amount = doc.get("rounded_total") or doc.grand_total
        allocated_amount = min(amount - advance_allocated, d.amount)
        advance_allocated += flt(allocated_amount)

        advance_row = {
            "doctype": doc.doctype + " Advance",
            "reference_type": d.reference_type,
            "reference_name": d.reference_name,
            "reference_row": d.reference_row,
            "remarks": d.remarks,
            "advance_amount": flt(d.amount),
            "allocated_amount": allocated_amount,
            "ref_exchange_rate": flt(d.exchange_rate),  # exchange_rate of advance entry
            "is_down_payment": d.get("down_payment"),
        }

        if d.get("paid_from"):
            advance_row["account"] = d.paid_from
        if d.get("paid_to"):
            advance_row["account"] = d.paid_to

        doc.append("advances", advance_row)

def get_advance_entries(doc, include_unallocated=True):
    if doc.doctype == "Sales Invoice":
        party_type = "Customer"
        party = doc.customer
        amount_field = "credit_in_account_currency"
        order_field = "sales_order"
        order_doctype = "Sales Order"
    else:
        party_type = "Supplier"
        party = doc.supplier
        amount_field = "debit_in_account_currency"
        order_field = "purchase_order"
        order_doctype = "Purchase Order"

    party_account = get_party_account(party_type, party=party, company=doc.company)

    order_list = list(set(d.get(order_field) for d in doc.get("items") if d.get(order_field)))

    journal_entries = get_advance_journal_entries(
        party_type, party, party_account, amount_field, order_doctype, order_list, include_unallocated
    )

    payment_entries = get_advance_payment_entries_for_regional(
        party_type, party, party_account, order_doctype, order_list, include_unallocated
    )

    res = journal_entries + payment_entries

    if doc.doctype == "Sales Invoice" and order_list:
        party_type = "Customer"
        party = doc.customer
        party_account = (get_party_account(party_type, party, doc.company),)
        amount_field = "credit_in_account_currency"
        order_doctype = "Sales Invoice"

        invoice_list = list(
            set(
                frappe.db.sql_list(
                    """
            SELECT si.name
            FROM `tabSales Invoice` si
            LEFT JOIN `tabSales Invoice Item` sii
            ON sii.parent = si.name
            WHERE si.is_down_payment_invoice = 1
            AND sii.sales_order in ({0})
            """.format(
                        ",".join([f'"{ol}"' for ol in order_list])
                    )
                )
            )
        )

        down_payments_je = get_advance_journal_entries(
            party_type,
            party,
            party_account,
            amount_field,
            order_doctype,
            invoice_list,
            include_unallocated,
        )

        down_payments_pe = get_advance_payment_entries(
            party_type, party, party_account, order_doctype, invoice_list, include_unallocated
        )

        res += down_payments_je + down_payments_pe

    return res



class AccountsControllerWithDownPayment(AccountsController):
    def set_total_advance_paid(self):
        frappe.throw('stop')
		ple = frappe.qb.DocType("Payment Ledger Entry")
		party = self.customer if self.doctype == "Sales Order" else self.supplier
		advance_query = (
			frappe.qb.from_(ple)
			.select(ple.account_currency, Abs(Sum(ple.amount_in_account_currency)).as_("amount"))
			.where((ple.party == party) & (ple.docstatus == 1) & (ple.company == self.company))
		)

		if self.doctype == "Sales Order":
			si = frappe.qb.DocType("Sales Invoice")
			sii = frappe.qb.DocType("Sales Invoice Item")
			down_payment_invoices = (
				frappe.qb.from_(si)
				.select(si.name)
				.left_join(sii)
				.on(sii.parent == si.name)
				.where((si.is_down_payment_invoice == 1) & (sii.sales_order == self.name))
				.run(as_list=True)
			)
			if down_payment_invoices and down_payment_invoices[0]:
				advance_query = advance_query.where(
					((ple.against_voucher_type == self.doctype) & (ple.against_voucher_no == self.name))
					| (
						(ple.against_voucher_type == "Sales Invoice")
						& (ple.against_voucher_no.isin(down_payment_invoices[0]))
					)
				)

		advance_query = advance_query.where(
			(ple.against_voucher_type == self.doctype) & (ple.against_voucher_no == self.name)
		)

		advance = advance_query.run(as_dict=True)

		if advance:
			advance = advance[0]

			advance_paid = flt(advance.amount, self.precision("advance_paid"))
			formatted_advance_paid = fmt_money(
				advance_paid, precision=self.precision("advance_paid"), currency=advance.account_currency
			)

			frappe.db.set_value(self.doctype, self.name, "party_account_currency", advance.account_currency)

			if advance.account_currency == self.currency:
				order_total = self.get("rounded_total") or self.grand_total
				precision = "rounded_total" if self.get("rounded_total") else "grand_total"
			else:
				order_total = self.get("base_rounded_total") or self.base_grand_total
				precision = "base_rounded_total" if self.get("base_rounded_total") else "base_grand_total"

			formatted_order_total = fmt_money(
				order_total, precision=self.precision(precision), currency=advance.account_currency
			)

			if self.currency == self.company_currency and advance_paid > order_total:
				frappe.throw(
					_(
						"Total advance ({0}) against Order {1} cannot be greater than the Grand Total ({2})"
					).format(formatted_advance_paid, self.name, formatted_order_total)
				)

			frappe.db.set_value(self.doctype, self.name, "advance_paid", advance_paid)
