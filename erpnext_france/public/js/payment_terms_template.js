frappe.ui.form.on("Payment Terms Template Detail", {
  payment_term: function (frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (row.payment_term) {
      frappe.db.get_value(
        "Payment Term",
        row.payment_term,
        ["custom_due_date_based_on_france", "custom_end_of_month_day"],
        function (value) {
          frappe.model.set_value(
            cdt,
            cdn,
            "custom_due_date_based_on_france",
            value.custom_due_date_based_on_france
          );
          frappe.model.set_value(
            cdt,
            cdn,
            "custom_end_of_month_day",
            value.custom_end_of_month_day
          );
        }
      );
    }
  },
});
