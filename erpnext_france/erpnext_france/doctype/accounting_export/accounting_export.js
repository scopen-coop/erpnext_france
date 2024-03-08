// Copyright (c) 2021, Britlog and contributors
// For license information, please see license.txt

frappe.ui.form.on('Accounting Export', {
    refresh: frm => {
        frm.disable_save();
        frm.page.set_primary_action('Export', () => {
            can_export(frm) ? export_data(frm) : null;
        });
        if (frm.doc.export_date === undefined) {
            frm.set_value('export_date', new Date());
        }
    }
});

const can_export = frm => {
    const company = frm.doc.company;
    const accounting_document = frm.doc.accounting_document;
    const from_date = frm.doc.from_date;
    const to_date = frm.doc.to_date;

    let is_valid_form = false;
    if (!company) {
        frappe.msgprint(__('Please select a company'));
    } else if (!accounting_document) {
        frappe.msgprint(__('Please select an accounting document'));
    } else if (!from_date) {
        frappe.msgprint(__('Please enter from date'));
    } else if (!to_date) {
        frappe.msgprint(__('Please enter to date'));
    } else {
        is_valid_form = true;
    }
    return is_valid_form;
};

const export_data = frm => {
    let get_template_url = '/api/method/erpnext_france.erpnext_france.doctype.accounting_export.exporter.export_data';
    var export_params = () => {
        return {
            company: frm.doc.company,
            accounting_document: frm.doc.accounting_document,
            from_date: frm.doc.from_date,
            to_date: frm.doc.to_date,
            export_date: frm.doc.export_date,
            included_already_exported_document: frm.doc.included_already_exported_document,
        };
    };

    open_url_post(get_template_url, export_params());
};
