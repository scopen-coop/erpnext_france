# Copyright (c) 2025, Scopen and Contributors
# See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime, flt
import uuid
from datetime import datetime


class SEPAPaymentBordereau(Document):
	def before_insert(self):
		"""Set naming series based on payment type"""
		if self.payment_type == "Debit":
			self.naming_series = "SEPA-DEBIT-.YYYY.-.####"
		else:
			self.naming_series = "SEPA-CREDIT-.YYYY.-.####"

	def validate(self):
		self.calculate_total()
		self.validate_lines()

	def on_update(self):
		status_changed_lines = False
		if not self.is_new() and self.get_doc_before_save():
			old_doc = self.get_doc_before_save()
			old_statuses = {d.name: d.status for d in old_doc.lines}
			for line in self.lines:
				old_status = old_statuses.get(line.name)
				if line.status != old_status and line.status in ["Accepted", "Rejected"]:
					from erpnext_france.regional.france.sepa_utils import reconcile_sepa_line_on_status_change
					reconcile_sepa_line_on_status_change(self, line, line.status)
					status_changed_lines = True
		
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

	def validate_lines(self):
		"""Validate that all lines have required data"""
		if self.status != "Draft":
			for line in self.lines:
				# Validate IBAN/BIC
				if not line.mandate and self.payment_type == "Debit":
					frappe.throw(_("Row {0}: SEPA Mandate is required for debit payments").format(line.idx))

				# Validate amounts
				if not line.amount or line.amount <= 0:
					frappe.throw(_("Row {0}: Amount must be greater than zero").format(line.idx))

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
		
		bank_account = frappe.get_doc("Bank Account", self.bank_account)
		if not bank_account.iban:
			frappe.throw(_("Company bank account {0} must have an IBAN").format(self.bank_account))
		if not bank_account.swift_number:
			frappe.throw(_("Company bank account {0} must have a BIC (Swift Number)").format(self.bank_account))

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
			fname=file_name,
			content=xml_content,
			dt=self.doctype,
			dn=self.name,
			is_private=1
		)

		self.sepa_file = file_doc.file_url
		self.status = "Exported"
		self.save()

		frappe.msgprint(_("SEPA file generated successfully"))
		return file_doc.file_url

	def generate_pain_008(self):
		"""Generate pain.008 XML for SEPA Direct Debit"""
		from lxml import etree

		# Get bank account details
		bank_account = frappe.get_doc("Bank Account", self.bank_account)

		# Create XML structure
		nsmap = {
			None: "urn:iso:std:iso:20022:tech:xsd:pain.008.001.02",
			"xsi": "http://www.w3.org/2001/XMLSchema-instance"
		}

		root = etree.Element("Document", nsmap=nsmap)
		cstmr_drct_dbt_initn = etree.SubElement(root, "CstmrDrctDbtInitn")

		# Group Header
		grp_hdr = etree.SubElement(cstmr_drct_dbt_initn, "GrpHdr")
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
		pmt_inf = etree.SubElement(cstmr_drct_dbt_initn, "PmtInf")
		pmt_inf_id = etree.SubElement(pmt_inf, "PmtInfId")
		pmt_inf_id.text = self.name
		pmt_mtd = etree.SubElement(pmt_inf, "PmtMtd")
		pmt_mtd.text = "DD"

		# Requested Collection Date
		reqd_colltn_dt = etree.SubElement(pmt_inf, "ReqdColltnDt")
		reqd_colltn_dt.text = str(self.execution_date)

		# Creditor (Company)
		cdtr = etree.SubElement(pmt_inf, "Cdtr")
		cdtr_nm = etree.SubElement(cdtr, "Nm")
		cdtr_nm.text = self.company

		# Creditor Account
		cdtr_acct = etree.SubElement(pmt_inf, "CdtrAcct")
		cdtr_acct_id = etree.SubElement(cdtr_acct, "Id")
		cdtr_acct_iban = etree.SubElement(cdtr_acct_id, "IBAN")
		cdtr_acct_iban.text = bank_account.iban.replace(" ", "")

		# Creditor Agent (BIC)
		cdtr_agt = etree.SubElement(pmt_inf, "CdtrAgt")
		fin_instn_id = etree.SubElement(cdtr_agt, "FinInstnId")
		bic = etree.SubElement(fin_instn_id, "BIC")
		bic.text = bank_account.swift_number

		# Direct Debit Transaction Information for each line
		for line in self.lines:
			mandate = frappe.get_doc("SEPA Mandate", line.mandate)
			mandate_bank_account = frappe.get_doc("Bank Account", mandate.bank_account)

			drct_dbt_tx_inf = etree.SubElement(pmt_inf, "DrctDbtTxInf")

			# Payment ID
			pmt_id = etree.SubElement(drct_dbt_tx_inf, "PmtId")
			end_to_end_id_elem = etree.SubElement(pmt_id, "EndToEndId")
			end_to_end_id_elem.text = line.end_to_end_id

			# Instructed Amount
			instd_amt = etree.SubElement(drct_dbt_tx_inf, "InstdAmt", Ccy="EUR")
			instd_amt.text = f"{line.amount:.2f}"

			# Direct Debit Transaction
			drct_dbt_tx = etree.SubElement(drct_dbt_tx_inf, "DrctDbtTx")
			mndt_rltd_inf = etree.SubElement(drct_dbt_tx, "MndtRltdInf")
			mndt_id = etree.SubElement(mndt_rltd_inf, "MndtId")
			mndt_id.text = mandate.rum
			dt_of_sgntr = etree.SubElement(mndt_rltd_inf, "DtOfSgntr")
			dt_of_sgntr.text = str(mandate.signature_date)

			# Debtor Agent (Customer's Bank)
			dbtr_agt = etree.SubElement(drct_dbt_tx_inf, "DbtrAgt")
			dbtr_fin_instn_id = etree.SubElement(dbtr_agt, "FinInstnId")
			dbtr_bic = etree.SubElement(dbtr_fin_instn_id, "BIC")
			dbtr_bic.text = mandate_bank_account.swift_number

			# Debtor (Customer)
			dbtr = etree.SubElement(drct_dbt_tx_inf, "Dbtr")
			dbtr_nm = etree.SubElement(dbtr, "Nm")
			dbtr_nm.text = line.party

			# Debtor Account
			dbtr_acct = etree.SubElement(drct_dbt_tx_inf, "DbtrAcct")
			dbtr_acct_id = etree.SubElement(dbtr_acct, "Id")
			dbtr_acct_iban = etree.SubElement(dbtr_acct_id, "IBAN")
			dbtr_acct_iban.text = mandate_bank_account.iban.replace(" ", "")

		return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")

	def generate_pain_001(self):
		"""Generate pain.001 XML for SEPA Credit Transfer"""
		from lxml import etree

		# Get bank account details
		bank_account = frappe.get_doc("Bank Account", self.bank_account)

		# Create XML structure
		nsmap = {
			None: "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03",
			"xsi": "http://www.w3.org/2001/XMLSchema-instance"
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
				as_dict=1
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

		return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")

	@frappe.whitelist()
	def mark_as_sent(self):
		"""Mark bordereau as sent to bank"""
		if self.status != "Exported":
			frappe.throw(_("Bordereau must be exported before marking as sent"))

		self.status = "Sent"
		self.save()
		frappe.msgprint(_("Bordereau marked as sent"))
