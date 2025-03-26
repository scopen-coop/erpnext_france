frappe.ui.form.on("Item", "onload", async function (frm) {
  frm.set_query("buy_account", "eco_part", set_accounts_filters);
  frm.set_query("sell_account", "eco_part", set_accounts_filters);
});

function set_accounts_filters() {
  return {
    filters: [
      ["Account", "is_group", "=", 0],
      [
        "Account",
        "account_type",
        "in",
        [
          "Tax",
          "Chargeable",
          "Income Account",
          "Expense Account",
          "Expenses Included In Valuation",
        ],
      ],
    ],
  };
}

