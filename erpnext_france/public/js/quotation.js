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
});

frappe.ui.form.on("Quotation", {
  payment_terms_template: function (frm) {
    if (!frm.doc.payment_terms_template) {
      frm.set_value("payment_schedule", []);
      return;
    }
    frappe.call({
      method:
        "erpnext_france.controllers.party.get_payment_terms_before_invoice",
      args: {
        doctype: frm.doc.doctype,
        grand_total: frm.doc.grand_total,
        base_grand_total: frm.doc.base_grand_total,
        posting_date: frm.doc.transaction_date,
        delivery_date: frm.doc.delivery_date,
        payment_terms_template: frm.doc.payment_terms_template,
      },
      callback: function (r) {
        if (r.message) {
          frm.set_value("payment_schedule", r.message);
        }
      },
    });
  },
});
