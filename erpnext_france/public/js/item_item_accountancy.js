// Copyright (c) 2023, Scopen and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item", {
  setup: function (frm) {
    frm.set_query(
      "categorie_comptable_tiers",
      "special_item_accountancy_code_details",
      function () {
        return { filters: { is_actif: 1 } };
      }
    );
  },
});
