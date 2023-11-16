// Copyright (c) 2022, Dokos SAS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Bank Transaction Categories"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			fieldname: "period",
			label: __("Period"),
			fieldtype: "Select",
			options: [
				{ "value": "this month", "label": __("This Month") },
				{ "value": "last month", "label": __("Last Month") },
				{ "value": "this quarter", "label": __("This quarter") },
				{ "value": "last quarter", "label": __("Last quarter") },
				{ "value": "this year", "label": __("This Year") },
				{ "value": "last year", "label": __("Last Year") },
			],
			default: "1 year",
			reqd: 1
		},
		{
			fieldname: "transaction_type",
			label: __("Transaction Type"),
			fieldtype: "Select",
			options: [
				{
					"label": __("Revenue"),
					"value": "credit"
				},
				{
					"label": __("Expense"),
					"value": "debit"
				}
			],
			reqd: 1
		},
	]
};
