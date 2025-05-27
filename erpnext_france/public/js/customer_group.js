// Copyright (c) 2025, Scopen and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer Group", "onload", function (frm) {
  frm.set_query("payment_terms", function () {
    return {
      filters: {
        template_payment_terms_before_invoice: 0,
      },
    };
  });
});
