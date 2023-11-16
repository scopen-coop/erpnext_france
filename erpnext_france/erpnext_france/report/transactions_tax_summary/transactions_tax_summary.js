// Copyright (c) 2021, Dokos SAS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Transactions Tax Summary"] = {
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value || "", row, column, data);
		if (data && data.indent == 0) {
			if (column.id == "base_grand_total" && data.difference != 0) {
				value = $(value).append(`<span class="text-danger"> (${format_currency(data.difference, null, 2)})</span>`)
			} else {
				value = $(`<span>${value}</span>`);
			}

			var $value = $(value).css("font-weight", "bold");
			value = $value.wrap("<p></p>").parent().html();
		}

		return value;
	},
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"period_start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.nowdate(), -3),
			"reqd": 1
		},
		{
			"fieldname":"period_end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.nowdate(),
			"reqd": 1
		},
		{
			"fieldname":"transaction_type",
			"label": __("Transaction Type"),
			"fieldtype": "Select",
			"default": "Sales Invoice",
			"options": [{"label": __("Sales Invoice"), "value": "Sales Invoice"}, {"label": __("Purchase Invoice"), "value": "Purchase Invoice"}]
		}
	]
};
