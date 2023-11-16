// Copyright (c) 2019, Dokos SAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sepa Mandate', {
	refresh: function(frm) {
		frm.trigger("toggle_reqd_fields")

		if (frm.doc.status != "Cancelled" && !frm.doc.registered_on_gocardless) {
			frm.add_custom_button(__("Cancel this mandate"), () => {
				frm.set_value("status", "Cancelled");
				frm.save()
			})
		}
	},
	registered_on_gocardless: function(frm) {
		frm.trigger("toggle_reqd_fields")
	},
	toggle_reqd_fields: function(frm) {
		frm.toggle_reqd("creation_date", !frm.doc.registered_on_gocardless)
		frm.toggle_reqd("bank_account", !frm.doc.registered_on_gocardless)
	}
});
