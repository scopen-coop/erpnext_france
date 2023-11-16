// Copyright (c) 2021, scopen.fr and contributors
// For license information, please see license.txt


frappe.ui.form.on("Purchase Invoice", {
        refresh: function (frm) {
            // @dokos
            if (frm.doc.docstatus === 1) {
                frm.add_custom_button(__('Accounting Journal Adjustment'), () => {
                    frappe.require("assets/erpnext_france/js/accounting_journal_adjustment.js", () => {
                        new erpnext.journalAdjustment({doctype: frm.doctype, docnames: [frm.docname]})
                    });
                }, __('Create'), true);
            }
            // @dokos
        }
    }
);
