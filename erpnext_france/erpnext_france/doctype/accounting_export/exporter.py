# -*- coding: utf-8 -*-
# Copyright (c) 2021, Britlog and Contributors
# Copyright (c) 20212023, Scopen and Contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import csv

import frappe
import frappe.permissions
from frappe import _
from frappe.utils import format_datetime
from frappe.utils.csvutils import UnicodeWriter
from six import StringIO


@frappe.whitelist()
def export_data(company=None, accounting_document=None, from_date=None, to_date=None, export_date=None,
				included_already_exported_document=None):

	exporter = DataExporter(company=company, accounting_document=accounting_document, from_date=from_date,
							to_date=to_date, export_date=export_date,
							included_already_exported_document=included_already_exported_document)
	exporter.build_response()


class DataExporter:
	def __init__(self, company=None, accounting_document=None, from_date=None, to_date=None, export_date=None,
				 included_already_exported_document=None):
		self.company = company
		self.accounting_document = accounting_document
		self.from_date = from_date
		self.to_date = to_date
		self.export_date = export_date
		self.included_already_exported_document = included_already_exported_document
		self.file_format = frappe.db.get_value("Company", self.company, "export_file_format")
		self.journal_code = ''

	def build_response(self):

		if self.file_format == "CIEL":
			self.writer = UnicodeWriter(quoting=csv.QUOTE_NONE)

		if self.file_format == "SAGE":
			self.queue = StringIO()
			self.writer = csv.writer(self.queue, delimiter=';')

		self.get_jounal_code()
		if self.journal_code == "" or self.journal_code is None:
			frappe.respond_as_web_page(_("Accounting Export Not Possible"),
									   _("Please Set Accounting Jounal For Purchases and Sales"),
									   indicator_color='orange')
			return

		self.add_data()
		if not self.data or len(self.data) == 0:
			frappe.respond_as_web_page(_('No Data'), _('There is no data to be exported'), indicator_color='orange')
			return

		# write out response
		if self.file_format == "CIEL":
			frappe.response['filename'] = 'XIMPORT.TXT'
			frappe.response['filecontent'] = self.writer.getvalue()
			frappe.response['type'] = 'binary'

		if self.file_format == "SAGE":
			frappe.response['filename'] = 'EXPORT.TXT'
			frappe.response['filecontent'] = self.queue.getvalue()
			frappe.response['type'] = 'binary'

	def get_jounal_code(self):
		try:
			if self.accounting_document == "Purchase Invoice":
				accounting_journal = frappe.db.get_value(
					"Accounting Journal",
					{'type': 'Purchase'},
					['journal_code'],
					as_dict=True
				)
			else:
				accounting_journal = frappe.db.get_value(
					"Accounting Journal",
					{'type': 'Sales'},
					['journal_code'],
					as_dict=True
				)
		except e:
			return

		self.journal_code = accounting_journal.journal_code


	def add_data(self):
		def _set_export_date(doc_type=None, voucher_no=None, export_date=None):
			if (
				export_date is not None
				and export_date != ''
				and export_date != 'undefined'
				and doc_type is not None
				and voucher_no is not None
			):
				invoice = frappe.get_doc(doc_type, voucher_no)
				if invoice is not None:
					# Use db_set for performance issue
					# as it is a custom field created by this app bypass validation Invoice rule is OK
					invoice.db_set('accounting_export_date', export_date)


		gl = frappe.qb.DocType("GL Entry")
		acc = frappe.qb.DocType("Account", alias='acc')
		against_acc = frappe.qb.DocType("Account", alias='against_acc')
		supp = frappe.qb.DocType("Supplier")
		cust = frappe.qb.DocType("Customer")
		party_acc_cust = frappe.qb.DocType('Party Account', alias='party_acc_cust')
		party_acc_supp = frappe.qb.DocType('Party Account', alias='party_acc_supp')

		sql_already_exported = ''

		# get journal code and export date
		if self.accounting_document == "Purchase Invoice":
			inv = frappe.qb.DocType("Purchase Invoice")
			fields_inv = inv.bill_no.as_('orign_no')
		else:
			inv = frappe.qb.DocType("Sales Invoice")
			fields_inv = inv.po_no.as_('orign_no')

		sql = (
			frappe.qb.from_(gl)
			.select(
				gl.name,
				gl.posting_date,
				gl.debit,
				gl.credit,
				gl.voucher_no,
				gl.party_type,
				gl.party,
				gl.against_voucher_type,
				acc.account_number,
				acc.account_name,
				party_acc_supp.subledger_account.as_('supp_subl_acc'),
				supp.supplier_name,
				party_acc_cust.subledger_account.as_('cust_subl_acc'),
				cust.customer_name,
				inv.due_date.as_('due_date'),
				fields_inv
			).inner_join(acc)
			.on(gl.account == acc.name)
			.left_join(against_acc)
			.on(gl.against == against_acc.name)
			.left_join(supp)
			.on(gl.party == supp.name)
			.left_join(party_acc_supp)
			.on(supp.name == party_acc_supp.parent)
			.left_join(cust)
			.on(gl.party == cust.name)
			.left_join(party_acc_cust)
			.on(cust.name == party_acc_cust.parent)
			.inner_join(inv)
			.on(gl.voucher_no == inv.name)
			.where(gl.voucher_type == self.accounting_document)
			.where(gl.posting_date[self.from_date:self.to_date])
			.where(acc.account_type.notin(["Bank", "Cash"]))
			.where(against_acc.account_type.notin(["Bank", "Cash"]))
			.where((self.company == party_acc_supp.company) | (party_acc_supp.company.isnull()))
			.where((self.company == party_acc_cust.company) | (party_acc_cust.company.isnull()))

		)

		if self.included_already_exported_document == '0':
			sql = sql.where(inv.accounting_export_date.isnull())

		self.data = (sql).run(as_dict=True)

		# format row
		if self.file_format == "CIEL":
			for doc in self.data:
				row = self.add_row_ciel(doc)
				_set_export_date(self.accounting_document, doc.voucher_no, self.export_date)
				self.writer.writerow([row])

		if self.file_format == "SAGE":

			supplier_invoice_number = {}
			customer_invoice_number = {}
			supplier_invoice_supplier_name = {}
			customer_invoice_customer_name = {}

			for doc in self.data:
				if doc.against_voucher_type == 'Purchase Invoice':
					if doc.voucher_no not in supplier_invoice_supplier_name:
						supplier_invoice_supplier_name[doc.voucher_no] = doc.supplier_name
					if doc.voucher_no not in supplier_invoice_number:
						if doc.orign_no is None:
							supplier_invoice_number[doc.voucher_no] = doc.voucher_no
						else:
							supplier_invoice_number[doc.voucher_no] = doc.orign_no

				if doc.against_voucher_type == 'Sales Invoice':
					if doc.voucher_no not in customer_invoice_customer_name:
						customer_invoice_customer_name[doc.voucher_no] = doc.customer_name
					if doc.voucher_no not in customer_invoice_number:
						if doc.orign_no is None:
							customer_invoice_number[doc.voucher_no] = doc.voucher_no
						else:
							customer_invoice_number[doc.voucher_no] = doc.orign_no

			for doc in self.data:
				doc.invoice_number = doc.voucher_no

				if doc.voucher_no in supplier_invoice_number:
					doc.invoice_number = supplier_invoice_number[doc.voucher_no]

				if doc.voucher_no in customer_invoice_number:
					doc.invoice_number = customer_invoice_number[doc.voucher_no]

				if doc.voucher_no in supplier_invoice_supplier_name:
					doc.party = supplier_invoice_supplier_name[doc.voucher_no]

				if doc.voucher_no in customer_invoice_customer_name:
					doc.party = customer_invoice_customer_name[doc.voucher_no]

				row = self.add_row_sage(doc)
				_set_export_date(self.accounting_document, doc.voucher_no, self.export_date)
				self.writer.writerow(row)

	def add_row_ciel(self, doc):
		ecriture_num = '{:>5s}'.format(doc.get("name")[-5:])
		journal_code = '{:<2s}'.format(self.journal_code)
		ecriture_date = format_datetime(doc.get("posting_date"), "yyyyMMdd")

		if doc.get("against_voucher_type") == "Purchase Invoice":
			echeance_date = format_datetime(doc.get("due_date"), "yyyyMMdd") or ''
		elif doc.get("against_voucher_type") == "Sales Invoice":
			echeance_date = format_datetime(doc.get("due_date"), "yyyyMMdd") or ''
		else:
			echeance_date = '{:<8s}'.format("")

		piece_num = '{:<12s}'.format(doc.get("voucher_no"))

		if doc.get("party_type") == "Supplier":
			compte_num = '{}{:<8s}'.format("401", doc.get("supp_subl_acc") or '')
		elif doc.get("party_type") == "Customer":
			compte_num = '{}{:<8s}'.format("411", doc.get("cust_subl_acc") or '')
		else:
			compte_num = '{:<11s}'.format(doc.get("account_number") or '')

		libelle = '{}{:<17s}'.format("FACTURE ", doc.get("voucher_no")[:17])
		montant = '{:>13.2f}'.format(doc.get("debit")) if doc.get("debit") != 0 \
			else '{:>13.2f}'.format(doc.get("credit"))
		credit_debit = "D" if doc.get("debit") > 0 else "C"
		numero_pointage = piece_num
		code_analytic = '{:<6s}'.format("")

		if doc.get("party_type") in ("Supplier", "Customer"):
			libelle_compte = '{:<34s}'.format(doc.get("party") or '')[:34]
		else:
			libelle_compte = '{:<34s}'.format(doc.get("account_name") or '')[:34]

		euro = "O"

		row = [ecriture_num, journal_code, ecriture_date, echeance_date, piece_num, compte_num,
			   libelle, montant, credit_debit, numero_pointage, code_analytic, libelle_compte, euro]

		return ''.join(row)

	def add_row_sage(self, doc):
		journal_code = self.journal_code
		ecriture_date = format_datetime(doc.get("posting_date"), "ddMMyy")

		if doc.get("against_voucher_type") == "Purchase Invoice":
			echeance_date = format_datetime(doc.get("due_date"), "ddMMyy")
		elif doc.get("against_voucher_type") == "Sales Invoice":
			echeance_date = format_datetime(doc.get("due_date"), "ddMMyy")
		else:
			echeance_date = ''

		piece_num = '{:.17s}'.format(doc.get("invoice_number").replace("\n", " ").replace("\r", " "))
		compte_num = doc.get("account_number")
		ref_inv = '{:.13s}'.format(doc.get("voucher_no"))
		ref_inv_inv = ref_inv
		compte_num_aux = ''
		if doc.get("party_type") == "Supplier":
			compte_num_aux = format(doc.get("supp_subl_acc") or '')
		elif doc.get("party_type") == "Customer":
			compte_num_aux = format(doc.get("cust_subl_acc") or '')

		libelle = '{}{:.49s}'.format("FACT ", doc.get("party"))
		debit = '{:.2f}'.format(doc.get("debit")).replace(".", ",")
		credit = '{:.2f}'.format(doc.get("credit")).replace(".", ",")

		if doc.get("party_type") in ("Supplier", "Customer"):
			libelle_compte = '{:.17s}'.format(format(doc.get("party") or ''));
		else:
			libelle_compte = '{:.17s}'.format(format(doc.get("account_name") or ''));

		if doc.get("against_voucher_type") == "Purchase Invoice":
			ref_inv_inv = piece_num
			piece_num = ref_inv

		row = [journal_code,
			   ecriture_date,
			   compte_num,
			   ref_inv,
			   ref_inv_inv,
			   piece_num,
			   compte_num_aux,
			   libelle,
			   debit,
			   credit,
			   echeance_date]

		return row
