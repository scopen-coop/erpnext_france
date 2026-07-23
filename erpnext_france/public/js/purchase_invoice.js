// Copyright (c) 2021, scopen.fr and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Invoice", {
  refresh: function (frm) {
    // @dokos
    if (frm.doc.docstatus === 1) {
      frm.add_custom_button(
        __("Accounting Journal Adjustment"),
        () => {
          frappe.require(
            "assets/erpnext_france/js/accounting_journal_adjustment.js",
            () => {
              new erpnext.journalAdjustment({
                doctype: frm.doctype,
                docnames: [frm.docname],
              });
            }
          );
        },
        __("Create"),
        true
      );
      if (frm.doc.outstanding_amount > 0 && frm.doc.supplier) {
        frappe.db
          .get_list("Bank Account", {
            filters: {
              party_type: "Supplier",
              party: frm.doc.supplier,
              is_default: 1,
            },
            limit: 1,
          })
          .then((results) => {
            const has_bank = results && results.length > 0;
            if (has_bank) {
              frm.add_custom_button(
                __("Add to SEPA Bordereau"),
                function () {
                  add_to_sepa_bordereau(frm);
                },
                __("Actions")
              );
            }
          });
      }
    }
    // @dokos
  },
});

function add_to_sepa_bordereau(frm) {
  frappe.call({
    method:
      "erpnext_france.regional.france.sepa_utils.add_invoice_to_sepa_bordereau",
    args: {
      invoice_name: frm.doc.name,
      invoice_type: "Purchase Invoice",
    },
    callback: function (r) {
      if (r.message) {
        frappe.msgprint(
          __("Invoice added to SEPA Payment Bordereau {0}", [r.message])
        );
        frappe.set_route("Form", "SEPA Payment Bordereau", r.message);
      }
    },
  });
}
