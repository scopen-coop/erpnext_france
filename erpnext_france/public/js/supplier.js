// Copyright (c) 2021, scopen.fr and contributors
// For license information, please see license.txt

frappe.ui.form.on("Supplier", {
  setup: function (frm) {
    frm.set_query("categorie_comptable_tiers", function () {
      return {
        filters: {
          is_actif: 1,
        },
      };
    });
  },
});
