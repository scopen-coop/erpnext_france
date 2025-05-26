frappe.ui.form.on("Item", "onload", async function (frm) {
  frm.set_query("buy_account", "eco_part", () => set_ecopart_accounts_filters("Expense Account"));
  frm.set_query("sell_account", "eco_part", () => set_ecopart_accounts_filters("Income Account"));
});

function set_ecopart_accounts_filters(type) {
  return {
    filters: [
      ["Account", "is_group", "=", 0],
      ["Account", "account_type", "=", type],
    ],
  };
}