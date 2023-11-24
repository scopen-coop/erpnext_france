// Copyright (c) 2019, Dokos SAS and Contributors
// Copyright (c) 2023, Scopen and contributors
// For license information, please see license.txt

frappe.listview_settings['Payment Entry'] = {
	get_indicator: function(doc) {
		if (doc.docstatus == 1) {
			return [__(doc.status, null, "Payment Entry"), doc.status === "Reconciled" ? "green": "orange", `status,==,${doc.status}`];
		} else if (doc.docstatus == 0) {
			return [__(doc.status, null, "Payment Entry"), doc.status === "Draft" ? "red": "blue", `status,==,${doc.status}`];
		}
	},
	has_indicator_for_draft: true,
	onload: function(list_view) {
		if (list_view.page.fields_dict.party_type) {
			list_view.page.fields_dict.party_type.get_query = function() {
				return {
					"filters": {
						"name": ["in", Object.keys(frappe.boot.party_account_types)],
					}
				};
			};
		}

		frappe.require("assets/erpnext_france/js/accounting_journal_adjustment.js", () => {
			list_view.page.add_actions_menu_item(
				__("Accounting Journal Adjustment"),
				() => {
					const docnames = list_view.get_checked_items(true);
					new erpnext.journalAdjustment({doctype: list_view.doctype, docnames: docnames})
				},
				true
			);
		});
	}
};
