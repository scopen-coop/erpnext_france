// Copyright (c) 2019, Dokos SAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sepa Direct Debit Settings', {
	onload: function(frm) {
		frm.set_query("bank_account", function() {
			return {
				filters: {
					"is_company_account": 1,
					"company": frm.doc.company
				}
			}
		});
	}
});
