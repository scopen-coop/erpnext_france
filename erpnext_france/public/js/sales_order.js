// Copyright (c) 2021, Scopen and contributors
// For license information, please see license.txt
frappe.ui.form.on("Sales Order", "onload", function (frm) {
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
});