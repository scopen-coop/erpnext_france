// Copyright (c) 2025, Scopen and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Term", {
  custom_due_date_based_on_france: function (frm) {
    const standard_options = [
      "Day(s) after invoice date",
      "Day(s) after the end of the invoice month",
      "Month(s) after the end of the invoice month",
    ];
    if (standard_options.includes(frm.doc.custom_due_date_based_on_france)) {
      frm.set_value(
        "due_date_based_on",
        frm.doc.custom_due_date_based_on_france
      );
    } else {
      frm.set_value("due_date_based_on", "Day(s) after invoice date");
      frm.set_value("credit_days", 0);
      // laisser due_date_based_on à une valeur valide pour ERPNext
      // le calcul réel sera fait par notre code via custom_due_date_based_on_france
    }
  },
});
