// Copyright (c) 2021, scopen.fr and contributors
// For license information, please see license.txt

frappe.ui.form.on("Special Item Accountancy Code Default", {
  setup: function (frm) {
    frm.set_query(
      "categorie_comptable_tiers",
      "default_values",
      function (doc, cdt, cdn) {
        var filters = {
          is_actif: 1,
        };
        return {
          filters: filters,
        };
      }
    );
  },
});
