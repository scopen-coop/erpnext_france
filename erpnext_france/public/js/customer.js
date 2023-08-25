// Copyright (c) 2021, Britlog and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer", "subledger_account", function(frm,cdt,cdn) {
    if (frm.doc.accounts) {
        frm.doc.accounts.forEach(function (company_accounts) {
            frappe.db.get_value("Company", company_accounts.company, "export_file_format", (r) => {
                if (frm.doc.subledger_account.length > 8 && r.export_file_format == "CIEL") {
                    frappe.msgprint("La longueur maximale du compte auxiliaire est de 8 caractères");
                    frm.set_value("subledger_account", frm.doc.subledger_account.substring(0, 8));
                }
            });
        });
    }

});

frappe.ui.form.on("Customer", {
  custom_check_vat_id(frm) {
    frappe.call({
        method: "erpnext_france.check_vat.eu_vat.check_vat",
        args: {vat_id: frm.doc.tax_id},
        callback: function (r) {
          if (r.message)
            if (r.message.valid) {
                frappe.msgprint({
                    title: __('VAT Check OK'),
                    indicator: 'green',
                    message: __('Name: {0}, Adress:{1}',[r.message.name,r.message.address])
                });
            } else {
                frappe.msgprint({
                    title: __('Invalid VAT number'),
                    indicator: 'red',
                    message: __('Invalid VAT number')
                });
            }
        }
      })
  },
});
