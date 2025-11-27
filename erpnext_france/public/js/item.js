// Copyright (c) 2021, scopen.fr and contributors
// For license information, please see license.txt
frappe.ui.form.on("Item", {
  setup: function (frm) {
    frm.set_query(
      "categorie_comptable_tiers",
      "special_item_accountancy_code_details",
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
  onload: function (frm) {
    frm.set_query("buy_account", "eco_part", () =>
      set_ecopart_accounts_filters("Expense Account")
    );
    frm.set_query("sell_account", "eco_part", () =>
      set_ecopart_accounts_filters("Income Account")
    );
  },
});

function set_ecopart_accounts_filters(type) {
  return {
    filters: [
      ["Account", "is_group", "=", 0],
      ["Account", "account_type", "=", type],
    ],
  };
}
