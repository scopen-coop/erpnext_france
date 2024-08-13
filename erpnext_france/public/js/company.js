// Copyright (c) 2021, scopen.fr and contributors
// For license information, please see license.txt

frappe.ui.form.on("Company", {
  setup: function (frm) {
    frm.set_query("discount_supplier_account", function () {
      return {
        filters: {
          root_type: "Expense",
        },
      };
    });
  },
  refresh: function (frm) {
    if (
      !frm.is_new() &&
      frm.doc.country === "France" &&
      frm.has_perm("write")
    ) {
      frm.remove_custom_button(__("Create Tax Template"), __("Manage"));
      frm.add_custom_button(
        __("ERPNext France - Create Tax Template"),
        function () {
          frm.call({
            method:
              "erpnext_france.utils.create_tax_template.create_tax_template",
            doc: frm.doc,
            freeze: true,
            callback: function () {
              frappe.msgprint(
                __(
                  "Default tax templates for sales, purchase and items are created."
                )
              );
            },
          });
        },
        __("Manage")
      );
    }
  },
});
