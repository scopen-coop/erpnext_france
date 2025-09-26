# Copyright (c) 2024, Scopen and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.utils import flt

from erpnext.accounts.doctype.payment_terms_template.payment_terms_template import PaymentTermsTemplate


class PaymentTermsTemplateWithTermsBeforeInvoice(PaymentTermsTemplate):
	def validate(self):
		self.validate_invoice_portion_with_terms_before_invoice()
		self.validate_terms_with_terms_before_invoice()


	def validate_invoice_portion_with_terms_before_invoice(self):
		total_portion = 0
		if self.template_payment_terms_before_invoice:
			for term in self.payment_terms_before_invoice:
				total_portion += flt(term.get("invoice_portion", 0))
		else:
			for term in self.terms:
				total_portion += flt(term.get("invoice_portion", 0))

		if flt(total_portion, 2) != 100.00:
			frappe.msgprint(_("Combined invoice portion must equal 100%"), raise_exception=1, indicator="red")

	def validate_terms_with_terms_before_invoice(self):
		terms = []
		if self.template_payment_terms_before_invoice:
			for term in self.payment_terms_before_invoice:
				self.verify_rows(term, terms)
		else:
			for term in self.terms:
				self.verify_rows(term, terms)


	def verify_rows(self, term, terms):
		if self.allocate_payment_based_on_payment_terms and not term.get('payment_term'):
			frappe.throw(_("Row {0}: Payment Term is mandatory").format(term.get('idx')))
		if self.template_payment_terms_before_invoice:
			return

		term_info = (
			term.get('payment_term'),
			term.get('credit_days'),
			term.get('credit_months'),
			term.get('due_date_based_on')
		)
		if term_info in terms:
			frappe.msgprint(
				_("The Payment Term at row {0} is possibly a duplicate.").format(term.idx),
				raise_exception=1,
				indicator="red",
			)
		else:
			terms.append(term_info)
