# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.utils import format_datetime
from frappe.utils.data import get_datetime_in_timezone

COLUMNS = [
	{
		"label": _("JournalCode"),
		"fieldname": "JournalCode",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": _("JournalLib"),
		"fieldname": "JournalLib",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": _("EcritureNum"),
		"fieldname": "EcritureNum",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": _("EcritureDate"),
		"fieldname": "EcritureDate",
		"fieldtype": "Date",
		"width": 90,
	},
	{
		"label": _("CompteNum"),
		"fieldname": "CompteNum",
		"fieldtype": "Link",
		"options": "Account",
		"width": 100,
	},
	{
		"label": _("CompteLib"),
		"fieldname": "CompteLib",
		"fieldtype": "Link",
		"options": "Account",
		"width": 200,
	},
	{
		"label": _("CompAuxNum"),
		"fieldname": "CompAuxNum",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": _("CompAuxLib"),
		"fieldname": "CompAuxLib",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": _("PieceRef"),
		"fieldname": "PieceRef",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": _("EcritureLib"),
		"fieldname": "EcritureLib",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": _("Debit"),
		"fieldname": "Debit",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": _("Credit"),
		"fieldname": "Credit",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": _("EcritureLet"),
		"fieldname": "EcritureLet",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": _("DateLet"),
		"fieldname": "DateLet",
		"fieldtype": "Date",
		"width": 90,
	},
	{
		"label": _("ValidDate"),
		"fieldname": "ValidDate",
		"fieldtype": "Date",
		"width": 90,
	},
	{
		"label": _("Montantdevise"),
		"fieldname": "Montantdevise",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": _("Idevise"),
		"fieldname": "Idevise",
		"fieldtype": "Data",
		"width": 90,
	},
	{
		"label": _("Export Date"),
		"fieldname": "ExportDate",
		"fieldtype": "Datetime",
		"width": 90,
	},
	{
		"label": _("GL Entry"),
		"fieldname": "GlName",
		"fieldtype": "Link",
		"options": "GL Entry",
		"width": 0,
	},
]


def execute(filters=None):
	validate_filters(filters)
	return COLUMNS, get_result(
		company=filters["company"],
		fiscal_year=filters["fiscal_year"],
		from_date=filters["from_date"],
		to_date=filters["to_date"],
		hide_already_exported=True if filters.get("hide_already_exported") else False
	)


def validate_filters(filters):
	if not filters.get("company"):
		frappe.throw(_("{0} is mandatory").format(_("Company")))

	if not filters.get("fiscal_year"):
		frappe.throw(_("{0} is mandatory").format(_("Fiscal Year")))


def get_gl_entries(company, fiscal_year, from_date, to_date, hide_already_exported):
	gle = frappe.qb.DocType("GL Entry")
	sales_invoice = frappe.qb.DocType("Sales Invoice")
	purchase_invoice = frappe.qb.DocType("Purchase Invoice")
	journal_entry = frappe.qb.DocType("Journal Entry")
	payment_entry = frappe.qb.DocType("Payment Entry")
	customer = frappe.qb.DocType("Customer")
	supplier = frappe.qb.DocType("Supplier")
	employee = frappe.qb.DocType("Employee")

	debit = frappe.query_builder.functions.Sum(gle.debit).as_("debit")
	credit = frappe.query_builder.functions.Sum(gle.credit).as_("credit")
	debit_currency = frappe.query_builder.functions.Sum(gle.debit_in_account_currency).as_(
		"debitCurr"
	)
	credit_currency = frappe.query_builder.functions.Sum(gle.credit_in_account_currency).as_(
		"creditCurr"
	)

	query = (
		frappe.qb.from_(gle)
		.left_join(sales_invoice)
		.on(gle.voucher_no == sales_invoice.name)
		.left_join(purchase_invoice)
		.on(gle.voucher_no == purchase_invoice.name)
		.left_join(journal_entry)
		.on(gle.voucher_no == journal_entry.name)
		.left_join(payment_entry)
		.on(gle.voucher_no == payment_entry.name)
		.left_join(customer)
		.on(gle.party == customer.name)
		.left_join(supplier)
		.on(gle.party == supplier.name)
		.left_join(employee)
		.on(gle.party == employee.name)
		.select(
			gle.posting_date.as_("GlPostDate"),
			gle.name.as_("GlName"),
			gle.account,
			gle.transaction_date,
			gle.export_date.as_("ExportDate"),
			debit,
			credit,
			debit_currency,
			credit_currency,
			gle.accounting_entry_number,
			gle.voucher_type,
			gle.voucher_no,
			gle.against_voucher_type,
			gle.against_voucher,
			gle.account_currency,
			gle.against,
			gle.party_type,
			gle.party,
			gle.accounting_journal,
			gle.remarks,
			sales_invoice.name.as_("InvName"),
			sales_invoice.title.as_("InvTitle"),
			sales_invoice.posting_date.as_("InvPostDate"),
			purchase_invoice.name.as_("PurName"),
			purchase_invoice.title.as_("PurTitle"),
			purchase_invoice.posting_date.as_("PurPostDate"),
			journal_entry.cheque_no.as_("JnlRef"),
			journal_entry.posting_date.as_("JnlPostDate"),
			journal_entry.title.as_("JnlTitle"),
			payment_entry.name.as_("PayName"),
			payment_entry.posting_date.as_("PayPostDate"),
			payment_entry.title.as_("PayTitle"),
			customer.customer_name,
			customer.name.as_("cusName"),
			supplier.supplier_name,
			supplier.name.as_("supName"),
			employee.employee_name,
			employee.name.as_("empName"),
		)
		.where((gle.company == company) & (gle.fiscal_year == fiscal_year))
		.where((gle.posting_date >= from_date) & (gle.posting_date <= to_date))
	)

	if hide_already_exported:
		query = query.where(gle.export_date.isnull())

	query = (
		query.groupby(gle.voucher_type, gle.voucher_no, gle.account, gle.name, gle.accounting_entry_number)
		.orderby(gle.posting_date, gle.voucher_no, gle.accounting_entry_number)
	)

	return query.run(as_dict=True)


def get_result(company, fiscal_year, from_date, to_date, hide_already_exported):
	data = get_gl_entries(company, fiscal_year, from_date, to_date, hide_already_exported)

	result = []

	company_currency = frappe.get_cached_value("Company", company, "default_currency")
	accounts = frappe.get_all(
		"Account",
		filters={"Company": company},
		fields=["name", "account_number", "account_name"],
	)
	journals = {
		j.journal_code: j.journal_name
		for j in frappe.get_all("Accounting Journal", fields=["journal_code", "journal_name"])
	}

	party_data = [x for x in data if x.get("against_voucher")]


	for d in data:
		JournalCode = d.get("accounting_journal") or re.split("-|/|[0-9]", d.get("voucher_no"))[0]
		EcritureNum = d.get("accounting_entry_number")
		GlName = d.get("GlName")

		EcritureDate = format_datetime(d.get("GlPostDate"), "yyyyMMdd")
		ExportDate = format_datetime(d.get("ExportDate"), "yyyy-MM-dd HH:mm")

		account_number = [
			{"account_number": account.account_number, "account_name": account.account_name}
			for account in accounts
			if account.name == d.get("account") and account.account_number
		]
		if account_number:
			CompteNum = account_number[0]["account_number"]
			CompteLib = account_number[0]["account_name"]
		else:
			frappe.throw(
				_(
					"Account number for account {0} is not available.<br> Please setup your Chart of Accounts correctly."
				).format(d.get("account"))
			)

		if d.get("party_type") == "Customer":
			CompAuxNum = d.get("cusName")
			CompAuxLib = d.get("customer_name")

		elif d.get("party_type") == "Supplier":
			CompAuxNum = d.get("supName")
			CompAuxLib = d.get("supplier_name")

		elif d.get("party_type") == "Employee":
			CompAuxNum = d.get("empName")
			CompAuxLib = d.get("employee_name")

		elif d.get("party_type") == "Student":
			CompAuxNum = d.get("stuName")
			CompAuxLib = d.get("student_name")

		elif d.get("party_type") == "Member":
			CompAuxNum = d.get("memName")
			CompAuxLib = d.get("member_name")

		else:
			CompAuxNum = ""
			CompAuxLib = ""

		ValidDate = format_datetime(d.get("GlPostDate"), "yyyyMMdd")

		PieceRef = d.get("voucher_no") or "Sans Reference"
		PieceRefType = d.get("voucher_type") or "Sans Reference"

		# EcritureLib is the reference title unless it is an opening entry
		if d.get("is_opening") == "Yes":
			EcritureLib = _("Opening Entry Journal")
		elif d.get("remarks") and d.get("remarks").lower() not in ("no remarks", _("no remarks")):
			EcritureLib = d.get("remarks")
		elif d.get("voucher_type") == "Sales Invoice":
			EcritureLib = d.get("InvTitle")
		elif d.get("voucher_type") == "Purchase Invoice":
			EcritureLib = d.get("PurTitle")
		elif d.get("voucher_type") == "Journal Entry":
			EcritureLib = d.get("JnlTitle")
		elif d.get("voucher_type") == "Payment Entry":
			EcritureLib = d.get("PayTitle")
		else:
			EcritureLib = d.get("voucher_type")

		EcritureLib = " ".join(EcritureLib.splitlines())

		debit = "{:.2f}".format(d.get("debit")).replace(".", ",")

		credit = "{:.2f}".format(d.get("credit")).replace(".", ",")

		if d.debit == d.credit == 0:
			continue

		Idevise = d.get("account_currency")

		DateLet = get_date_let(d, party_data) if d.get("against_voucher") else None
		EcritureLet = d.get("against_voucher", "") if DateLet else ""

		Montantdevise = None
		if Idevise != company_currency:
			Montantdevise = (
				"{:.2f}".format(d.get("debitCurr")).replace(".", ",")
				if d.get("debitCurr") != 0
				else "{:.2f}".format(d.get("creditCurr")).replace(".", ",")
			)
		else:
			Montantdevise = (
				"{:.2f}".format(d.get("debit")).replace(".", ",")
				if d.get("debit") != 0
				else "{:.2f}".format(d.get("credit")).replace(".", ",")
			)

		row = [
			JournalCode,
			journals.get(JournalCode),
			EcritureNum,
			EcritureDate,
			CompteNum,
			d.get("account"),
			CompAuxNum,
			CompAuxLib,
			PieceRef,
			EcritureLib,
			debit,
			credit,
			EcritureLet,
			DateLet or "",
			ValidDate,
			Montantdevise,
			Idevise,
			ExportDate,
			GlName
		]

		result.append(row)

	return result

def get_date_let(d, data):
	let_dates = [
		x.get("GlPostDate")
		for x in data
		if (
			x.get("against_voucher") == d.get("against_voucher")
			and x.get("against_voucher_type") == d.get("against_voucher_type")
			and x.get("party") == d.get("party")
		)
	]

	if not let_dates or len(let_dates) == 1:
		let_vouchers = frappe.get_all(
			"GL Entry",
			filters={
				"against_voucher": d.get("against_voucher"),
				"against_voucher_type": d.get("against_voucher_type"),
				"party": d.get("party"),
			},
			fields=["posting_date"],
		)

		if len(let_vouchers) > 1:
			return format_datetime(max([x.get("posting_date") for x in let_vouchers]), "yyyyMMdd")

	return format_datetime(max(let_dates), "yyyyMMdd") if len(let_dates) > 1 else None
