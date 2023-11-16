// Copyright (c) 2023, Dokos SAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Recurrence Period", {
	setup(frm) {
		frm.set_query("billing_interval", () => {
			return {
				filters: {"name": ["in", ["Day", "Week", "Month", "Year"]]}
			};
		});
	},
});
