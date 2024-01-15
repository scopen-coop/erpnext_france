// Copyright (c) 2021, Scopen and contributors
// For license information, please see license.txt
frappe.provide("erpnext");

frappe.ui.form.on('Sales Invoice', {
    is_down_payment_invoice: async function (frm) {
        if (frm.doc.is_down_payment_invoice) {
            const so = [...new Set(frm.doc.items.map(line => {
                    return line.sales_order;
                }))];
            frm.set_value("items", []);

            let total = await frappe.db.get_value("Sales Order", so[0], ["grand_total"]);
            total = total.message.grand_total;

            let down_payment_items = await frappe.db.get_list("Item",
                {
                    fields: [
                        'item_name',
                        'item_code',
                        'stock_uom',
                        'is_down_payment_item',
                        'down_payment_percentage',
                        'description'
                    ],
                    filters: {is_down_payment_item: 1}
                }
            );

            let down_payment_item = down_payment_items[0];
            let down_payment_item_defaults = await frappe.db.get_list("Item Default",
                    {
                        fields: ['company', 'income_account'],
                        filters: {parent: down_payment_item.item_code}
                    }
            );

            let down_payment_item_default = down_payment_item_defaults[0];

            down_payment_item.sales_order = so[0];
            down_payment_item.rate = parseFloat(total) * parseFloat(down_payment_item.down_payment_percentage) / 100;
            down_payment_item.qty = 1;
            down_payment_item.amount = down_payment_item.rate;
            down_payment_item.uom = down_payment_item.stock_uom;
            down_payment_item.conversion_factor = 1;
            down_payment_item.income_account = down_payment_item_default.income_account;
            down_payment_item.down_payment_rate = down_payment_item.down_payment_percentage;

            frm.add_child("items", down_payment_item);
            frm.refresh_field("items");

            frm.set_value("taxes_and_charges", null);
            frm.set_value("taxes", []);
        }
    },

    customer: function (frm) {
        if (frm.doc.is_pos) {
            var pos_profile = frm.doc.pos_profile;
        }

        if (frm.updating_party_details)
            return;

        if (frm.doc.__onload && frm.doc.__onload.load_after_mapping)
            return;

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
    },

    get_down_payment: function (frm) {
        if (!frm.is_return && frm.doc.docstatus < 1) {
            return frappe.call({
                method: "erpnext_france.controllers.accounts_controller.get_down_payment",
                args: {
                    doc: frm.doc
                },
                callback:async function (r) {
                    if (r.message) {
                        frm.set_value('advances', []);
                        
                        for (let row of r.message.advances) {

                            frm.add_child('advances', {
                                advance_amount: row.advance_amount,
                                allocated_amount: row.allocated_amount,
                                reference_type: row.reference_type,
                                reference_name: row.reference_name,
                                remarks: row.remarks,
                                reference_row: row.reference_row,
                                is_down_payment: row.is_down_payment,
                                exchange_gain_loss: row.exchange_gain_loss,
                                ref_exchange_rate: row.ref_exchange_rate
                            });
                        }

                        frm.refresh_field("advances");

                        let outstanding_amount = parseFloat(frm.doc.grand_total) - parseFloat(frm.doc.total_advance);
                        await frm.cscript.calculate_taxes_and_totals(outstanding_amount);
                    }
                }
            });
        }
    }
});


frappe.ui.form.on('Sales Invoice Item', {
    sales_order: function (frm, cdt, cdn) {
        calculate_down_payment(locals[cdt][cdn]);
    },
    is_down_payment_item: function (frm, cdt, cdn) {
        calculate_down_payment(locals[cdt][cdn]);
    },
    down_payment_rate: function (frm, cdt, cdn) {
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
