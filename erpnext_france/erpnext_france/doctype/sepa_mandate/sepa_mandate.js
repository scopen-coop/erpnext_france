// Copyright (c) 2026, Scopen and contributors
// For license information, please see license.txt

frappe.ui.form.on("SEPA Mandate", {
  refresh: function (frm) {
    // Add button to update to recurring
    if (frm.doc.sequence_type === "FRST" && frm.doc.status === "Active") {
      frm.add_custom_button(__("Update to Recurring"), function () {
        frappe.call({
          method: "update_to_recurring",
          doc: frm.doc,
          callback: function (r) {
            frm.reload_doc();
          },
        });
      });
    }

    // Set color indicator based on status
    if (frm.doc.status) {
      var color_map = {
        Draft: "gray",
        Active: "green",
        Cancelled: "red",
      };
      frm.page.set_indicator(frm.doc.status, color_map[frm.doc.status]);
    }
  },

  customer: function (frm) {
    // Set query for bank account to only show customer's bank accounts
    if (frm.doc.customer) {
      frm.set_query("bank_account", function () {
        return {
          filters: {
            party_type: "Customer",
            party: frm.doc.customer,
          },
        };
      });
    }
  },

  onload: function (frm) {
    // Set query for bank account
    if (frm.doc.customer) {
      frm.trigger("customer");
    }
  },

  bank_account: function (frm) {
    // Fetch IBAN and BIC when bank account is selected
    if (frm.doc.bank_account) {
      frappe.db.get_value(
        "Bank Account",
        frm.doc.bank_account,
        ["iban", "swift_number"],
        function (r) {
          if (r) {
            if (!r.iban || !r.swift_number) {
              frappe.msgprint(
                __("Please ensure IBAN and BIC are filled in the bank account")
              );
            }
          }
        }
      );
    }
  },
});
