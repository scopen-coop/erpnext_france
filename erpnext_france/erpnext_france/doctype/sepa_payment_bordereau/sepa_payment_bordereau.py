# Copyright (c) 2025, Scopen and Contributors
# See license.txt

import uuid
from datetime import datetime

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, get_datetime, now_datetime


class SEPAPaymentBordereau(Document):
	def before_insert(self):
		"""Set naming series based on payment type"""
		if self.payment_type == "Debit":
			self.naming_series = "SEPA-DEBIT-.YYYY.-.####"
		else:
			self.naming_series = "SEPA-CREDIT-.YYYY.-.####"

	def validate(self):
		self.calculate_total()
		self.validate_company_bank_account()
		self.validate_locked_lines()
		self.validate_lines()

	@staticmethod
	def is_line_locked(line):
		"""Invoice/amount/etc. locked once Accepted/Rejected or linked to a Payment Entry."""
		return bool(line.get("payment_entry")) or line.get("status") in ("Accepted", "Rejected")

	@staticmethod
	def is_status_locked(line):
		"""Status stays editable while Pending or Rejected; only Accepted is frozen."""
		return line.get("status") == "Accepted"

	def on_trash(self):
		from erpnext_france.regional.france.sepa_utils import sync_invoices_sepa_bordereau_links

		sync_invoices_sepa_bordereau_links(
			(line.invoice, line.invoice_type) for line in self.lines if line.invoice
		)

	def validate_company_bank_account(self):
		"""Bank account on the bordereau must be a company account, not a customer/supplier one."""
		if not self.company:
			return

		from erpnext_france.regional.france.sepa_utils import (
			ensure_bordereau_bank_account,
			is_company_bank_account,
		)

		if self.status == "Draft" and ensure_bordereau_bank_account(self):
			return

		if self.bank_account and not is_company_bank_account(self.bank_account, self.company):
			frappe.throw(
				_(
					"Bank Account {0} is not a company bank account. Please select your company's bank account."
				).format(self.bank_account)
			)

	def on_update(self):
		status_changed_lines = False
		invoices_to_sync = {(line.invoice, line.invoice_type) for line in self.lines if line.invoice}

		if not self.is_new() and self.get_doc_before_save():
			old_doc = self.get_doc_before_save()
			old_statuses = {d.name: d.status for d in old_doc.lines}
			invoices_to_sync.update(
				(line.invoice, line.invoice_type) for line in old_doc.lines if line.invoice
			)
			for line in self.lines:
				old_status = old_statuses.get(line.name)
				if line.status != old_status and line.status in ["Accepted", "Rejected"]:
					from erpnext_france.regional.france.sepa_utils import reconcile_sepa_line_on_status_change

					reconcile_sepa_line_on_status_change(self, line, line.status)
					status_changed_lines = True

		from erpnext_france.regional.france.sepa_utils import sync_invoices_sepa_bordereau_links

		sync_invoices_sepa_bordereau_links(invoices_to_sync)

		# Update overall bordereau status if needed
		if status_changed_lines and self.lines:
			statuses = [line.status for line in self.lines]
			new_status = self.status
			if all(status == "Accepted" for status in statuses):
				new_status = "Closed"
			elif "Accepted" in statuses and "Rejected" in statuses:
				new_status = "Partial Rejections"
			elif all(status == "Rejected" for status in statuses):
				new_status = "Exported"

			if new_status != self.status:
				self.db_set("status", new_status)

	def calculate_total(self):
		"""Calculate total amount from all lines"""
		total = 0
		for line in self.lines:
			total += flt(line.amount)
		self.total_amount = total

	def validate_locked_lines(self):
		"""Prevent edits on processed lines, while still allowing status changes on Pending/Rejected."""
		if self.is_new() or not self.get_doc_before_save():
			return

		old_lines = {d.name: d for d in self.get_doc_before_save().lines}
		immutable_data_fields = (
			"invoice",
			"invoice_type",
			"party",
			"party_type",
			"amount",
			"mandate",
			"end_to_end_id",
			"payment_entry",
		)

		for line in self.lines:
			old_line = old_lines.get(line.name)
			if not old_line:
				continue

			# Allow unlocking Accepted lines when their Payment Entry was cancelled
			unlocked_accepted = (
				old_line.status == "Accepted"
				and old_line.payment_entry
				and frappe.db.get_value("Payment Entry", old_line.payment_entry, "docstatus") == 2
				and not line.payment_entry
				and line.status == "Pending"
			)
			if unlocked_accepted:
				continue

			if self.is_status_locked(old_line) and line.status != old_line.status:
				frappe.throw(
					_("Row {0}: Accepted lines cannot change status").format(line.idx)
				)

			if not self.is_line_locked(old_line):
				continue

			for fieldname in immutable_data_fields:
				old_value = old_line.get(fieldname)
				new_value = line.get(fieldname)
				if fieldname == "amount":
					changed = flt(old_value) != flt(new_value)
				else:
					changed = new_value != old_value
				if changed:
					frappe.throw(
						_(
							"Row {0}: Accepted/Rejected lines linked to a Payment Entry cannot be modified"
						).format(line.idx)
					)

			# rejection_reason stays editable on Rejected lines
			if old_line.status == "Accepted" and line.rejection_reason != old_line.rejection_reason:
				frappe.throw(
					_("Row {0}: Accepted lines cannot be modified").format(line.idx)
				)

		# Prevent deletion of locked lines
		current_names = {line.name for line in self.lines if line.name}
		for name, old_line in old_lines.items():
			if name not in current_names and self.is_line_locked(old_line):
				frappe.throw(
					_("Accepted/Rejected lines linked to a Payment Entry cannot be removed")
				)

	def validate_lines(self):
		"""Validate that all lines have required data"""
		from erpnext_france.regional.france.sepa_utils import validate_invoice_unique_in_bordereaux

		seen_invoices = set()

		for line in self.lines:
			self.sync_line_from_payment_type(line)

			if line.invoice:
				line_key = (line.invoice, line.invoice_type)
				if line_key in seen_invoices:
					frappe.throw(
						_("Row {0}: Invoice {1} appears more than once in this bordereau").format(
							line.idx, line.invoice
						)
					)
				seen_invoices.add(line_key)

				validate_invoice_unique_in_bordereaux(
					line.invoice,
					line.invoice_type,
					current_bordereau=self.name,
					current_line_name=line.name if line.name else None,
				)

			if self.payment_type == "Credit" and line.party:
				supplier_bank_account = frappe.db.exists(
					"Bank Account",
					{"party_type": "Supplier", "party": line.party, "is_default": 1},
				)
				if not supplier_bank_account:
					frappe.throw(
						_("Row {0}: Supplier {1} does not have a default bank account").format(
							line.idx, line.party
						)
					)

		if self.status != "Draft":
			for line in self.lines:
				if not line.mandate and self.payment_type == "Debit":
					frappe.throw(_("Row {0}: SEPA Mandate is required for debit payments").format(line.idx))

				if not line.amount or line.amount <= 0:
					frappe.throw(_("Row {0}: Amount must be greater than zero").format(line.idx))

	def sync_line_from_payment_type(self, line):
		"""Keep line party/invoice types aligned with bordereau payment type."""
		if self.payment_type == "Credit":
			expected_invoice_type = "Purchase Invoice"
			expected_party_type = "Supplier"
			party_field = "supplier"
		else:
			expected_invoice_type = "Sales Invoice"
			expected_party_type = "Customer"
			party_field = "customer"

		# Already processed lines keep their stored values; do not re-check outstanding
		# (partial validation would fail on invoices already paid by a previous accept).
		if self.is_line_locked(line):
			if not line.invoice_type:
				line.invoice_type = expected_invoice_type
			if not line.party_type:
				line.party_type = expected_party_type
			return

		line.invoice_type = expected_invoice_type
		line.party_type = expected_party_type

		if not line.invoice:
			return

		invoice = frappe.db.get_value(
			line.invoice_type,
			line.invoice,
			[party_field, "outstanding_amount", "company", "docstatus"],
			as_dict=True,
		)
		if not invoice:
			frappe.throw(_("Row {0}: Invoice {1} does not exist").format(line.idx, line.invoice))

		if invoice.docstatus != 1:
			frappe.throw(_("Row {0}: Invoice {1} must be submitted").format(line.idx, line.invoice))

		if self.company and invoice.company != self.company:
			frappe.throw(_("Row {0}: Invoice {1} belongs to another company").format(line.idx, line.invoice))

		# Outstanding is only enforced while composing the bordereau.
		# After export/send, invoices may already be paid (partial accept or external payment)
		# and must not block status updates on remaining pending lines.
		if self.status == "Draft" and flt(invoice.outstanding_amount) <= 0:
			frappe.throw(_("Row {0}: Invoice {1} has no outstanding amount").format(line.idx, line.invoice))

		line.party = invoice.get(party_field)
		if not line.amount:
			line.amount = invoice.outstanding_amount

		if self.payment_type == "Debit" and line.party and not line.mandate:
			line.mandate = frappe.db.get_value("Customer", line.party, "sepa_mandate")

	def before_submit(self):
		"""Generate End-to-End IDs for all lines before validation"""
		self.generate_end_to_end_ids()

	@frappe.whitelist()
	def validate_bordereau(self):
		"""Validate the bordereau and change status to Validated"""
		if self.status != "Draft":
			frappe.throw(_("Only draft bordereaux can be validated"))

		# Generate End-to-End IDs
		self.generate_end_to_end_ids()

		# Check Company bank account
		if not self.bank_account:
			frappe.throw(_("Please select a bank account for the bordereau"))

		self.validate_company_bank_account()

		bank_account = frappe.get_doc("Bank Account", self.bank_account)
		if not bank_account.iban:
			frappe.throw(_("Company bank account {0} must have an IBAN").format(self.bank_account))
		if not bank_account.swift_number:
			frappe.throw(
				_("Company bank account {0} must have a BIC (Swift Number)").format(self.bank_account)
			)

		# Check ICS for direct debit
		if self.payment_type == "Debit":
			company_ics = frappe.db.get_value("Company", self.company, "sepa_ics")
			if not company_ics:
				frappe.throw(
					_("Please set the SEPA Creditor Identifier (ICS) on company {0}").format(self.company)
				)

		# Perform all validations
		for line in self.lines:
			# Check IBAN/BIC
			if self.payment_type == "Debit":
				if not line.mandate:
					frappe.throw(_("Row {0}: SEPA Mandate is required for debit payments").format(line.idx))

				# Check mandate status
				mandate = frappe.get_doc("SEPA Mandate", line.mandate)
				if mandate.status != "Active":
					frappe.throw(_("Row {0}: SEPA Mandate must be active").format(line.idx))

			# Validate amounts
			if not line.amount or line.amount <= 0:
				frappe.throw(_("Row {0}: Amount must be greater than zero").format(line.idx))

		# Update status
		self.status = "Validated"
		self.save()
		frappe.msgprint(_("Bordereau validated successfully"))

	def generate_end_to_end_ids(self):
		"""Generate unique End-to-End IDs for all lines"""
		for line in self.lines:
			if not line.end_to_end_id:
				# Generate unique End-to-End ID
				# Format: COMPANY-YYYYMMDD-UUID (max 35 chars for SEPA)
				timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
				unique_id = str(uuid.uuid4())[:8].upper()
				line.end_to_end_id = f"{self.company[:10]}-{timestamp}-{unique_id}"

	@frappe.whitelist()
	def generate_sepa_file(self):
		"""Generate SEPA XML file (pain.008 for debit, pain.001 for credit)"""
		if self.status not in ["Validated", "Exported"]:
			frappe.throw(_("Bordereau must be validated before generating SEPA file"))

		if self.payment_type == "Debit":
			xml_content = self.generate_pain_008()
		else:
			xml_content = self.generate_pain_001()

		# Save the XML file
		from frappe.utils.file_manager import save_file

		file_name = f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
		file_doc = save_file(
			fname=file_name, content=xml_content, dt=self.doctype, dn=self.name, is_private=1
		)

		self.sepa_file = file_doc.file_url
		self.status = "Exported"
		self.save()

		frappe.msgprint(_("SEPA file generated successfully"))
		return file_doc.file_url

	def generate_pain_008(self):
		"""Generate pain.008 XML for SEPA Direct Debit"""
		from lxml import etree

		from erpnext_france.regional.france.sepa_utils import (
			add_pain_remittance_info,
			get_sepa_line_remittance_info,
		)

		# Get bank account and company ICS
		bank_account = frappe.get_doc("Bank Account", self.bank_account)
		company_ics = frappe.db.get_value("Company", self.company, "sepa_ics")
		if not company_ics:
			frappe.throw(
				_("Please set the SEPA Creditor Identifier (ICS) on company {0}").format(self.company)
			)

		# Group lines by (mandate_type, sequence_type) — pain.008 requires one PmtInf per SeqTp
		groups = {}
		for line in self.lines:
			mandate = frappe.get_doc("SEPA Mandate", line.mandate)
			key = (mandate.mandate_type, mandate.sequence_type)
			if key not in groups:
				groups[key] = []
			groups[key].append((line, mandate))

		nsmap = {
			None: "urn:iso:std:iso:20022:tech:xsd:pain.008.001.02",
			"xsi": "http://www.w3.org/2001/XMLSchema-instance",
		}

		root = etree.Element("Document", nsmap=nsmap)
		cstmr_drct_dbt_initn = etree.SubElement(root, "CstmrDrctDbtInitn")

		# Group Header (totals across all groups)
		grp_hdr = etree.SubElement(cstmr_drct_dbt_initn, "GrpHdr")
		etree.SubElement(grp_hdr, "MsgId").text = self.name
		etree.SubElement(grp_hdr, "CreDtTm").text = now_datetime().strftime("%Y-%m-%dT%H:%M:%S")
		etree.SubElement(grp_hdr, "NbOfTxs").text = str(len(self.lines))
		etree.SubElement(grp_hdr, "CtrlSum").text = f"{self.total_amount:.2f}"
		initg_pty = etree.SubElement(grp_hdr, "InitgPty")
		etree.SubElement(initg_pty, "Nm").text = self.company

		# One PmtInf per (mandate_type, sequence_type) group
		for (mandate_type, sequence_type), group_lines in groups.items():
			group_total = sum(flt(line.amount) for line, _ in group_lines)

			pmt_inf = etree.SubElement(cstmr_drct_dbt_initn, "PmtInf")
			etree.SubElement(pmt_inf, "PmtInfId").text = f"{self.name}-{mandate_type}-{sequence_type}"
			etree.SubElement(pmt_inf, "PmtMtd").text = "DD"
			etree.SubElement(pmt_inf, "NbOfTxs").text = str(len(group_lines))
			etree.SubElement(pmt_inf, "CtrlSum").text = f"{group_total:.2f}"

			# Payment Type Information (required: SvcLvl, LclInstrm, SeqTp)
			pmt_tp_inf = etree.SubElement(pmt_inf, "PmtTpInf")
			svc_lvl = etree.SubElement(pmt_tp_inf, "SvcLvl")
			etree.SubElement(svc_lvl, "Cd").text = "SEPA"
			lcl_instrm = etree.SubElement(pmt_tp_inf, "LclInstrm")
			etree.SubElement(lcl_instrm, "Cd").text = mandate_type  # CORE or B2B
			etree.SubElement(pmt_tp_inf, "SeqTp").text = sequence_type  # FRST or RCUR

			etree.SubElement(pmt_inf, "ReqdColltnDt").text = str(self.execution_date)

			# Creditor (Company)
			cdtr = etree.SubElement(pmt_inf, "Cdtr")
			etree.SubElement(cdtr, "Nm").text = self.company

			# Creditor Account
			cdtr_acct = etree.SubElement(pmt_inf, "CdtrAcct")
			cdtr_acct_id = etree.SubElement(cdtr_acct, "Id")
			etree.SubElement(cdtr_acct_id, "IBAN").text = bank_account.iban.replace(" ", "")

			# Creditor Agent (BIC)
			cdtr_agt = etree.SubElement(pmt_inf, "CdtrAgt")
			fin_instn_id = etree.SubElement(cdtr_agt, "FinInstnId")
			etree.SubElement(fin_instn_id, "BIC").text = bank_account.swift_number

			# Direct Debit Transaction Information for each line in this group
			for line, mandate in group_lines:
				mandate_bank_account = frappe.get_doc("Bank Account", mandate.bank_account)

				if mandate_bank_account.get("iban") is None:
					frappe.throw(_("Missing IBAN information for {0}").format(mandate_bank_account.name))

				if mandate_bank_account.get("swift_number") is None:
					frappe.throw(_("Missing SWIFT information for {0}").format(mandate_bank_account.name))

				drct_dbt_tx_inf = etree.SubElement(pmt_inf, "DrctDbtTxInf")

				pmt_id = etree.SubElement(drct_dbt_tx_inf, "PmtId")
				etree.SubElement(pmt_id, "EndToEndId").text = line.end_to_end_id

				instd_amt = etree.SubElement(drct_dbt_tx_inf, "InstdAmt", Ccy="EUR")
				instd_amt.text = f"{line.amount:.2f}"

				# Direct Debit Transaction: mandate info + creditor scheme ID (ICS)
				drct_dbt_tx = etree.SubElement(drct_dbt_tx_inf, "DrctDbtTx")
				mndt_rltd_inf = etree.SubElement(drct_dbt_tx, "MndtRltdInf")
				etree.SubElement(mndt_rltd_inf, "MndtId").text = mandate.rum
				etree.SubElement(mndt_rltd_inf, "DtOfSgntr").text = str(mandate.signature_date)

				cdtr_schme_id = etree.SubElement(drct_dbt_tx, "CdtrSchmeId")
				cdtr_schme_id_id = etree.SubElement(cdtr_schme_id, "Id")
				prvt_id = etree.SubElement(cdtr_schme_id_id, "PrvtId")
				othr = etree.SubElement(prvt_id, "Othr")
				etree.SubElement(othr, "Id").text = company_ics
				schme_nm = etree.SubElement(othr, "SchmeNm")
				etree.SubElement(schme_nm, "Prtry").text = "SEPA"

				# Debtor Agent (Customer's Bank)
				dbtr_agt = etree.SubElement(drct_dbt_tx_inf, "DbtrAgt")
				dbtr_fin_instn_id = etree.SubElement(dbtr_agt, "FinInstnId")
				etree.SubElement(dbtr_fin_instn_id, "BIC").text = mandate_bank_account.swift_number

				# Debtor (Customer)
				dbtr = etree.SubElement(drct_dbt_tx_inf, "Dbtr")
				etree.SubElement(dbtr, "Nm").text = line.party

				# Debtor Account
				dbtr_acct = etree.SubElement(drct_dbt_tx_inf, "DbtrAcct")
				dbtr_acct_id = etree.SubElement(dbtr_acct, "Id")
				etree.SubElement(dbtr_acct_id, "IBAN").text = mandate_bank_account.iban.replace(" ", "")

				add_pain_remittance_info(
					drct_dbt_tx_inf,
					get_sepa_line_remittance_info(line),
				)

		return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")

	def generate_pain_001(self):
		"""Generate pain.001 XML for SEPA Credit Transfer"""
		from lxml import etree

		from erpnext_france.regional.france.sepa_utils import (
			add_pain_remittance_info,
			get_sepa_line_remittance_info,
		)

		# Get bank account details
		bank_account = frappe.get_doc("Bank Account", self.bank_account)

		# Create XML structure
		nsmap = {
			None: "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03",
			"xsi": "http://www.w3.org/2001/XMLSchema-instance",
		}

		root = etree.Element("Document", nsmap=nsmap)
		cstmr_cdt_trf_initn = etree.SubElement(root, "CstmrCdtTrfInitn")

		# Group Header
		grp_hdr = etree.SubElement(cstmr_cdt_trf_initn, "GrpHdr")
		msg_id = etree.SubElement(grp_hdr, "MsgId")
		msg_id.text = self.name
		cre_dt_tm = etree.SubElement(grp_hdr, "CreDtTm")
		cre_dt_tm.text = now_datetime().strftime("%Y-%m-%dT%H:%M:%S")
		nb_of_txs = etree.SubElement(grp_hdr, "NbOfTxs")
		nb_of_txs.text = str(len(self.lines))
		ctrl_sum = etree.SubElement(grp_hdr, "CtrlSum")
		ctrl_sum.text = f"{self.total_amount:.2f}"

		# Initiating Party
		initg_pty = etree.SubElement(grp_hdr, "InitgPty")
		nm = etree.SubElement(initg_pty, "Nm")
		nm.text = self.company

		# Payment Information
		pmt_inf = etree.SubElement(cstmr_cdt_trf_initn, "PmtInf")
		pmt_inf_id = etree.SubElement(pmt_inf, "PmtInfId")
		pmt_inf_id.text = self.name
		pmt_mtd = etree.SubElement(pmt_inf, "PmtMtd")
		pmt_mtd.text = "TRF"

		# Payment Type Information must be defined at lot level in pain.001.001.03
		pmt_tp_inf = etree.SubElement(pmt_inf, "PmtTpInf")
		svc_lvl = etree.SubElement(pmt_tp_inf, "SvcLvl")
		svc_lvl_cd = etree.SubElement(svc_lvl, "Cd")
		svc_lvl_cd.text = "SEPA"

		# Requested Execution Date
		reqd_exctn_dt = etree.SubElement(pmt_inf, "ReqdExctnDt")
		reqd_exctn_dt.text = str(self.execution_date)

		# Debtor (Company)
		dbtr = etree.SubElement(pmt_inf, "Dbtr")
		dbtr_nm = etree.SubElement(dbtr, "Nm")
		dbtr_nm.text = self.company

		# Debtor Account
		dbtr_acct = etree.SubElement(pmt_inf, "DbtrAcct")
		dbtr_acct_id = etree.SubElement(dbtr_acct, "Id")
		dbtr_acct_iban = etree.SubElement(dbtr_acct_id, "IBAN")
		dbtr_acct_iban.text = bank_account.iban.replace(" ", "")

		# Debtor Agent (BIC)
		dbtr_agt = etree.SubElement(pmt_inf, "DbtrAgt")
		fin_instn_id = etree.SubElement(dbtr_agt, "FinInstnId")
		bic = etree.SubElement(fin_instn_id, "BIC")
		bic.text = bank_account.swift_number

		# Credit Transfer Transaction Information for each line
		for line in self.lines:
			# Get supplier bank account
			supplier_bank_account = frappe.db.get_value(
				"Bank Account",
				{"party_type": "Supplier", "party": line.party, "is_default": 1},
				["name", "iban", "swift_number"],
				as_dict=1,
			)

			if not supplier_bank_account:
				frappe.throw(_("Default bank account not found for supplier {0}").format(line.party))

			cdt_trf_tx_inf = etree.SubElement(pmt_inf, "CdtTrfTxInf")

			# Payment ID
			pmt_id = etree.SubElement(cdt_trf_tx_inf, "PmtId")
			end_to_end_id_elem = etree.SubElement(pmt_id, "EndToEndId")
			end_to_end_id_elem.text = line.end_to_end_id

			# Amount
			amt = etree.SubElement(cdt_trf_tx_inf, "Amt")
			instd_amt = etree.SubElement(amt, "InstdAmt", Ccy="EUR")
			instd_amt.text = f"{line.amount:.2f}"

			# Creditor Agent (Supplier's Bank)
			cdtr_agt = etree.SubElement(cdt_trf_tx_inf, "CdtrAgt")
			cdtr_fin_instn_id = etree.SubElement(cdtr_agt, "FinInstnId")
			cdtr_bic = etree.SubElement(cdtr_fin_instn_id, "BIC")
			cdtr_bic.text = supplier_bank_account.swift_number

			# Creditor (Supplier)
			cdtr = etree.SubElement(cdt_trf_tx_inf, "Cdtr")
			cdtr_nm = etree.SubElement(cdtr, "Nm")
			cdtr_nm.text = line.party

			# Creditor Account
			cdtr_acct = etree.SubElement(cdt_trf_tx_inf, "CdtrAcct")
			cdtr_acct_id = etree.SubElement(cdtr_acct, "Id")
			cdtr_acct_iban = etree.SubElement(cdtr_acct_id, "IBAN")
			cdtr_acct_iban.text = supplier_bank_account.iban.replace(" ", "")

			add_pain_remittance_info(
				cdt_trf_tx_inf,
				get_sepa_line_remittance_info(line),
			)

		ns = {"ns": "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"}
		invalid_tx_pmt_tp_inf = root.xpath(
			"/ns:Document/ns:CstmrCdtTrfInitn/ns:PmtInf/ns:CdtTrfTxInf/ns:PmtTpInf",
			namespaces=ns,
		)
		if invalid_tx_pmt_tp_inf:
			frappe.throw(
				_(
					"Invalid pain.001.001.03: PmtTpInf is forbidden at transaction level "
					"(/Document/CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtTpInf)."
				)
			)

		pmt_inf_nodes = root.xpath("/ns:Document/ns:CstmrCdtTrfInitn/ns:PmtInf", namespaces=ns)
		lot_pmt_tp_inf = root.xpath("/ns:Document/ns:CstmrCdtTrfInitn/ns:PmtInf/ns:PmtTpInf", namespaces=ns)
		if len(lot_pmt_tp_inf) != len(pmt_inf_nodes):
			frappe.throw(
				_("Invalid pain.001.001.03: each PmtInf must contain exactly one " "PmtTpInf at lot level.")
			)

		return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")

	@frappe.whitelist()
	def mark_as_sent(self):
		"""Mark bordereau as sent to bank"""
		if self.status != "Exported":
			frappe.throw(_("Bordereau must be exported before marking as sent"))

		self.status = "Sent"
		self.save()
		frappe.msgprint(_("Bordereau marked as sent"))

	@frappe.whitelist()
	def accept_selected_lines(self, line_names):
		"""Accept selected pending lines and create payment entries."""
		import json

		if isinstance(line_names, str):
			line_names = json.loads(line_names)

		if not line_names:
			frappe.throw(_("Please select at least one line"))

		from erpnext_france.regional.france.sepa_utils import (
			reconcile_sepa_line_on_status_change,
			sync_invoice_sepa_bordereau_link,
			update_bordereau_status,
		)

		line_names_set = set(line_names)
		results = {"success": [], "failed": [], "skipped": []}

		for line in self.lines:
			if line.name not in line_names_set:
				continue

			if line.status == "Accepted":
				results["skipped"].append(
					{
						"name": line.name,
						"invoice": line.invoice,
						"reason": _("Already accepted"),
					}
				)
				continue

			if line.payment_entry:
				pe_docstatus = frappe.db.get_value("Payment Entry", line.payment_entry, "docstatus")
				if pe_docstatus == 1:
					results["skipped"].append(
						{
							"name": line.name,
							"invoice": line.invoice,
							"reason": _("Payment Entry already linked"),
						}
					)
					continue

			if line.status != "Pending":
				results["skipped"].append(
					{
						"name": line.name,
						"invoice": line.invoice,
						"reason": _("Line is not pending"),
					}
				)
				continue

			savepoint = f"sepa_accept_{line.name}"
			try:
				frappe.db.savepoint(savepoint)
				reconcile_sepa_line_on_status_change(self, line, "Accepted", silent=True)
				frappe.db.set_value(
					"SEPA Payment Bordereau Line",
					line.name,
					"status",
					"Accepted",
					update_modified=False,
				)
				sync_invoice_sepa_bordereau_link(line.invoice, line.invoice_type)
				results["success"].append({"name": line.name, "invoice": line.invoice})
			except Exception as e:
				frappe.db.rollback(save_point=savepoint)
				results["failed"].append(
					{
						"name": line.name,
						"invoice": line.invoice,
						"reason": str(e),
					}
				)

		update_bordereau_status(self.name)

		return results
