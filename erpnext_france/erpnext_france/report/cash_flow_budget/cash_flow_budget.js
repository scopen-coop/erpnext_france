// Copyright (c) 2022, Dokos SAS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cash Flow Budget"] = {
	"collapse_all_rows": 1,
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "bank_account",
			"label": __("Bank Account"),
			"fieldtype": "Link",
			"options": "Bank Account",
			"default": frappe.boot.sysdefaults.default_bank_account_name,
			"get_query": function () {
				var company = frappe.query_report.get_filter_value('company')
				return {
					filters: {
						company: company
					}
				}
			},
			"reqd": 1
		},
		{
			"fieldname": "period_end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.add_months(frappe.datetime.month_start(), 6), -1),
			"reqd": 1,
			"min_date": frappe.datetime.now_date(true)
		},
		{
			"fieldname": "scenario",
			"label": __("Scenario"),
			"fieldtype": "Link",
			"options": "Cash Flow Forecast Scenario"
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column && column.fieldname == "label") {
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");

			value = $value.wrap("<p></p>").parent().html();
		}

		return value;
	},
	get_datatable_options(options) {
		return Object.assign(options, {
			tabulator_options: {
				dataTreeStartExpanded: false,
				rowFormatter:function(row){
					const data = row.getData();
					const element = row.getElement()

					if (element.classList.contains("tabulator-row-even")) {
						row.getElement().style.backgroundColor = "#fff";
					}

					if(data.bold){
						row.getElement().style.backgroundColor = "#f9f9f9";
					}
				},
			}
		})
	},
	after_datatable_render(datatable) {
		var withIcon = function(cell, formatterParams, onRendered){
			const value = cell.getValue()
			const data = cell.getData()
			let formattedValue = value;

			if (data.can_be_edited) {
				formattedValue = `<strong>${value}   ${frappe.utils.icon('edit', 'xs')}</strong>`;
			}

			if (data.can_be_deleted) {
				formattedValue = `${value}   ${frappe.utils.icon('delete', 'xs')}`;
			}

			onRendered(function() {
				cell.getElement().addEventListener("click", () => {

					if (data.can_be_edited) {
						const category = value.split(" ")
						const target_dt = "Cash Flow Forecast Entry"

						let new_doc = frappe.model.get_new_doc(target_dt);
						new_doc.category = category[1]

						const after_insert = () => {
							frappe.set_route("query-report", "Cash Flow Budget")
							frappe.query_report.refresh();
						}

						frappe.ui.form.make_quick_entry(
							target_dt,
							after_insert,
							null,
							new_doc,
							null
						)
					} else if (data.can_be_deleted) {
						frappe.db.delete_doc(data.doctype, data.docname).then(() => {
							frappe.query_report.refresh();
						});
					}
				});
			});

			return formattedValue;
		};

		setTimeout(() => {
			const label_column = datatable.table.getColumn("label")
			label_column.updateDefinition({
				formatter: withIcon
			})
		}, 2000);
	}
};
