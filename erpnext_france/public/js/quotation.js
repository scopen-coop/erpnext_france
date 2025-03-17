frappe.ui.form.on("Quotation", "onload", function (frm) {
  frm.set_query("payment_terms_template", function () {
    return {
      filters: {
        template_payment_terms_before_invoice: 1,
      },
    };
  });
  frm.set_query("payment_term", "payment_schedule", function (frm, cdt, cdn) {
    return {
      filters: {
        payment_terms_before_invoice: 1,
      },
    };
  });

  // Hide Due Date on quotation
//  let payment_schedule_grid = frm.get_field("payment_schedule").grid;
//  payment_schedule_grid.set_column_disp("due_date", false);
});
