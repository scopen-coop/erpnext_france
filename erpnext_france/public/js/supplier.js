// Copyright (c) 2021, Britlog and contributors
// For license information, please see license.txt

frappe.ui.form.on("Supplier", "subledger_account", function(frm,cdt,cdn) {
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