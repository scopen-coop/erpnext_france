// Copyright (c) 2021, Scopen and contributors
// For license information, please see license.txt
frappe.provide("erpnext");

frappe.ui.form.on('Sales Invoice', {
    is_down_payment_invoice: function(frm) {
		if (frm.doc.is_down_payment_invoice) {
			const so = [...new Set(frm.doc.items.map(line => {
				return line.sales_order
			}))]
			
            frm.set_value("items", []);
            
			so.map(value => {
				const d = frm.add_child("items");
				d.sales_order = value;
			})
			
            frm.refresh_field("items");

			frappe.db.get_list("Item", {filters: {is_down_payment_item: 1}})
			.then(r => {
				if (r.length == 1) {
					frm.doc.items.forEach(line => {
						frappe.model.set_value(line.doctype, line.name, "item_code", r[0].name);
					})
				}
			})
		}
	},
    
    customer: function(frm) {
        if (frm.doc.is_pos){
			var pos_profile = frm.doc.pos_profile;
		}

        if(frm.updating_party_details) return;

		if (frm.doc.__onload && frm.doc.__onload.load_after_mapping) return;
        
        erpnext.utils.get_party_details(frm,
			"erpnext_france.controllers.party.get_party_details", {
				posting_date: frm.doc.posting_date,
				party: frm.doc.customer,
				party_type: "Customer",
				account: frm.doc.debit_to,
				price_list: frm.doc.selling_price_list,
				pos_profile: pos_profile,
				down_payment: frm.doc.is_down_payment_invoice
			}
        ); // Missing me.apply_pricing_rule
    }
});


frappe.ui.form.on('Sales Invoice Item', {
	sales_order: function(frm, cdt, cdn) {
		calculate_down_payment(locals[cdt][cdn]);
	},
	is_down_payment_item: function(frm, cdt, cdn) {
		calculate_down_payment(locals[cdt][cdn]);
	},
	down_payment_rate: function(frm, cdt, cdn) {
		calculate_down_payment(locals[cdt][cdn]);
	},
	timesheets_remove(frm) {
		frm.trigger("calculate_timesheet_totals");
	}
});



const calculate_down_payment = line => {
	if (line.sales_order && line.is_down_payment_item) {
		frappe.db.get_value("Sales Order", line.sales_order, ["base_total", "total"], r => {
			frappe.model.set_value(line.doctype, line.name, "price_list_rate", flt(line.down_payment_rate) / 100.0 * flt(r.total))
			frappe.model.set_value(line.doctype, line.name, "base_rate", flt(line.down_payment_rate) / 100.0 * flt(r.base_total))
			frappe.model.set_value(line.doctype, line.name, "rate", flt(line.down_payment_rate) / 100.0 * flt(r.total))
		})
	}
}
