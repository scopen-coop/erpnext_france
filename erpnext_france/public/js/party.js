// Copyright (c) 2021, Britlog and contributors
// For license information, please see license.txt

frappe.ui.form.on(
  "Party Account",
  "subledger_account",
  function (frm, cdt, cdn) {
    if (frm.doc.accounts) {
      frm.doc.accounts.forEach(function (company_accounts) {
        let d = locals[cdt][cdn];
        frappe.db.get_value(
          "Company",
          company_accounts.company,
          "export_file_format",
          (r) => {
            if (
              d.subledger_account.length > 8 &&
              r.export_file_format === "CIEL"
            ) {
              frappe.model.set_value(
                cdt,
                cdn,
                "subledger_account",
                d.subledger_account.substring(0, 8)
              );
              frappe.msgprint(
                __(
                  "La longueur maximale du compte auxiliaire est de 8 caractères"
                )
              );
            }
          }
        );
      });
    }
  }
);
