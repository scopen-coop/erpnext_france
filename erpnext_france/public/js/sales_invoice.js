// Copyright (c) 2021, Scopen and contributors
// For license information, please see license.txt
frappe.provide("erpnext");

frappe.ui.form.on("Sales Invoice", {
  refresh: function (frm) {
    // Add button to add invoice to SEPA bordereau if eligible
    if (
      frm.doc.docstatus === 1 &&
      frm.doc.outstanding_amount > 0 &&
      frm.doc.customer
    ) {
      // Check if customer has SEPA mandate
      frappe.db.get_value("Customer", frm.doc.customer, "sepa_mandate", (r) => {
        if (r && r.sepa_mandate) {
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

    if (!frm.doc.is_down_payment_invoice) {
      return;
    }

    if (
      frm.doc.down_payment_type == "ByPercent" ||
      frm.doc.down_payment_value === frm.doc.grand_total
    ) {
      return;
    }
    frm.dashboard.set_headline_alert(
      __(
        "Warning: Rounding Issue when creating down payment invoice {0} instead of {1}",
        [frm.doc.grand_total, frm.doc.down_payment_value]
      ),
      "red"
    );
  },

  customer: function (frm) {
    if (frm.doc.is_pos) {
      var pos_profile = frm.doc.pos_profile;
    }

    if (frm.updating_party_details) return;

    if (frm.doc.__onload && frm.doc.__onload.load_after_mapping) return;

    erpnext.utils.get_party_details(
      frm,
      "erpnext_france.controllers.party.get_party_details",
      {
        posting_date: frm.doc.posting_date,
        party: frm.doc.customer,
        party_type: "Customer",
        account: frm.doc.debit_to,
        price_list: frm.doc.selling_price_list,
        pos_profile: pos_profile,
        down_payment: frm.doc.is_down_payment_invoice,
      }
    ); // Missing me.apply_pricing_rule
  },

  get_down_payment: function (frm) {
    if (!frm.is_return && frm.doc.docstatus < 1) {
      return frappe.call({
        method:
          "erpnext_france.controllers.accounts_controller.get_down_payment",
        args: {
          doc: frm.doc,
        },
        callback: function (r) {
          if (r.message) {
            frm.reload_doc();
          }
        },
      });
    }
  },
});

frappe.ui.form.on("Sales Invoice Item", {
  timesheets_remove(frm) {
    frm.trigger("calculate_timesheet_totals");
  },
});

frappe.ui.form.on("Sales Invoice", {
  customer: function (frm) {
    frm.trigger("payment_terms_template");
  },
  due_date: function (frm) {
    frm.trigger("payment_terms_template");
  },
});

function add_to_sepa_bordereau(frm) {
  frappe.call({
    method:
      "erpnext_france.regional.france.sepa_utils.add_invoice_to_sepa_bordereau",
    args: {
      invoice_name: frm.doc.name,
      invoice_type: "Sales Invoice",
    },
    callback: function (r) {
      if (r.message) {
        frappe.msgprint(
          __("Invoice added to SEPA Payment Bordereau {0}", [r.message])
        );
        // Navigate to the bordereau
        frappe.set_route("Form", "SEPA Payment Bordereau", r.message);
      }
    },
  });
}
