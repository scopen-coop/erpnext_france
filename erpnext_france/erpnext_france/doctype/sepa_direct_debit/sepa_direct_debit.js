// Copyright (c) 2019, DOKOS SAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sepa Direct Debit', {
	onload: function(frm) {
		if (frm.is_new()) {
			frm.set_value("from_date", frappe.datetime.month_start());
			frm.set_value("to_date", frappe.datetime.month_end());
			frm.set_value("total_amount", 0);
		}
	},
	refresh: function(frm) {
		if (frm.doc.docstatus==0 && frm.doc.mode_of_payment) {
			frm.trigger("add_payment_btn")
		}
	},
	company: function(frm) {
		if (frm.doc.company) {
			frm.set_value("currency", erpnext.get_currency(frm.doc.company));
			frappe.db.get_value("Sepa Direct Debit Settings", frm.doc.company, "mode_of_payment", r => {
				if (r) {
					frm.set_value("mode_of_payment", r.mode_of_payment);
				} else {
					frappe.msgprint(__("Please create <a href='/app/List/Sepa Direct Debit Settings/List'>Sepa Direct Debit Settings</a> for company {0}", [frm.doc.company]))
				}
			})
		}
	},
	get_payment_entries: function(frm) {
		return frappe.call({
			method: "get_payment_entries",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("payment_entries");
				frm.refresh_fields();

				$(frm.fields_dict.payment_entries.wrapper).find("[data-fieldname=amount]").each(function(i,v){
					if (i !=0){
						$(v).addClass("text-right")
					}
				})
			}
		});
	},
	generate_xml_file: function(frm) {
		if (frm.doc.direct_debit_type) {
			frm.save()
			return frappe.call({
				method: "generate_xml_file",
				doc: frm.doc,
				callback: function(r, rt) {
					if (r) {
						frm.reload_doc();
						frappe.show_alert({message: __("Your XML has been generated and added to the toolbar"), indicator: 'green'})
					}
				}
			});
		} else {
			frappe.msgprint(__("Please select a direct debit type"))
		}

	},
	mode_of_payment(frm) {
		if (frm.doc.docstatus==0 && frm.doc.mode_of_payment) {
			frm.trigger("add_payment_btn")
		}
	},
	add_payment_btn(frm) {
		frm.add_custom_button(__("Generate SEPA Payments"), function(){
			frappe.confirm(__("Automatically generate payment entries for all unpaid sales invoice with a due date between {0} and {1} for customers with a valid Sepa mandate ?", [frappe.datetime.obj_to_user(frm.doc.from_date), frappe.datetime.obj_to_user(frm.doc.to_date)]), () => {
				frappe.call({
					method: "erpnext_france.erpnext_france.doctype.sepa_direct_debit.sepa_direct_debit.create_sepa_payment_entries",
					args: {
						"from_date": frm.doc.from_date,
						"to_date": frm.doc.to_date,
						"mode_of_payment": frm.doc.mode_of_payment
					}
				}).then(r => {
					if (r == "Success") {
						frappe.show_alert({message:__("All missing SEPA payment entries have been generated"), indicator: 'green'});
					} else {
						frappe.show_alert({message:__("An error prevented the creation of all SEPA payment entries"), indicator: 'red'});
					}
				});
			})
		});
	}
});
