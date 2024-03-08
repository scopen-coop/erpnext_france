// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Fichier des Ecritures Comptables [FEC]"] = {
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
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
			"reqd": 1
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 0
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 0
		},
		{
			"fieldname": "hide_already_exported",
			"label": __("Hide Already Exported"),
			"fieldtype": "Check",
			"default": false,
			"reqd": 0
		},
	],
	onload: function (query_report) {
		query_report.page.add_inner_button(__("Export"), function () {
			if (query_report.columns) {
				let dialog = new frappe.ui.Dialog({
					title: 'Export FEC File',
					fields: [{
							label: 'Mark Gl Entry As Exported',
							fieldname: 'mark_exported',
							fieldtype: 'Check'
						}],
					size: 'small',
					primary_action_label: 'Export',
					primary_action(values) {
						fec_export(query_report, values.mark_exported);
						dialog.hide();
					}
				});
				dialog.show();
			} else {
				frappe.msgprint('Nothing to export');
			}
		});

		query_report.add_make_chart_button = function () {
			//
		};
	}
};

let fec_export = function (query_report, mark_exported) {
	const fiscal_year = query_report.get_values().fiscal_year;
	const company = query_report.get_values().company;
	frappe.db.get_value("Company", company, "siren_number", (value) => {
		const company_data = value.siren_number;
		if (company_data === null || company_data === undefined) {
			frappe.msgprint(__("Please register the SIREN number in the company information file"));
		} else {
			frappe.db.get_value("Fiscal Year", fiscal_year, "year_end_date", (r) => {
				const fy = r.year_end_date;
				const title = company_data + "FEC" + moment(fy).format('YYYYMMDD');
				// Remove unwanted columns in CSV Export
				const column_row = query_report.columns.filter(col => !['ExportDate', 'GlName'].includes(col.fieldname)).map(col => col.label);
				const column_data = query_report.get_data_for_csv(false);

				let gl_entries = [];
				column_data.forEach(data => {
					gl_entries.push([data.pop(), data.pop()])
				});

				const result = [column_row].concat(column_data);
				downloadify(result, null, title);

				if (mark_exported) {
					mark_as_exported(gl_entries);
				}
			});
		}
	});
};

let downloadify = function (data, roles, title) {
	if (roles && roles.length && !has_common(roles, roles)) {
		frappe.msgprint(__("Export not allowed. You need {0} role to export.", [frappe.utils.comma_or(roles)]));
		return;
	}

	const filename = title + ".csv";
	let csv_data = to_tab_csv(data);
	const a = document.createElement('a');

	if ("download" in a) {
		// Used Blob object, because it can handle large files
		let blob_object = new Blob([csv_data], {
			type: 'text/csv;charset=UTF-8'
		});
		a.href = URL.createObjectURL(blob_object);
		a.download = filename;

	} else {
		// use old method
		a.href = 'data:attachment/csv,' + encodeURIComponent(csv_data);
		a.download = filename;
		a.target = "_blank";
	}

	document.body.appendChild(a);
	a.click();

	document.body.removeChild(a);
};

let to_tab_csv = function (data) {
	let res = [];
	$.each(data, function (i, row) {
		res.push(row.join(";"));
	});
	return res.join("\n");
};


function mark_as_exported(gl_entries) {
	frappe.call({
		method: "erpnext_france.controllers.mark_gl_entry_as_exported.mark_gl_entry_as_exported",
		args: {gl_entries},
		callback: function (response) {
			if (!response || !response.message) {
				frappe.throw(__('No Response From Server'));
				return
			}

			if (response.message.error) {
				return
			}
		}
	});
}