// Copyright (c) 2021, Britlog and contributors
// For license information, please see license.txt

frappe.ui.form.on("ERPNext France Settings", {
  refresh: function (frm) {
    frappe
      .call(
        "erpnext_france.utils.create_down_payment_item.has_down_payment_item"
      )
      .then((r) => {
        if (r.message) {
          return;
        }
        frm.add_custom_button(
          __("ERPNext France - Create Down Payment Item"),
          function () {
            display_dialog_create_down_payment_item(
              frm,
              frappe.defaults.get_user_default("Company")
            );
          },
          __("Manage")
        );
      });
  },
});
