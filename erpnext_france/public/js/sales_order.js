// Copyright (c) 2021, Scopen and contributors
// For license information, please see license.txt
frappe.ui.form.on("Sales Order", "onload", async function (frm) {
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
//  await prevent_term_modification_if_payment_exist(frm)
});

frappe.ui.form.on("Sales Order", {
  delivery_date: function (frm) {
    frm.trigger('payment_terms_template');
  },
  transaction_date: function (frm) {
    frm.trigger('payment_terms_template');
  },
});


async function prevent_term_modification_if_payment_exist(frm) {
  let payments = await frappe.db.get_list('Payment Entry Reference', {
    fields: ['parent', 'payment_term', 'allocated_amount'],
    filters: {
      reference_doctype: 'Sales Order',
      reference_name: frm.doc.name
    }
  });

  let payments_array = payments.map((payment) => payment.payment_term);
  for (idx in frm.doc.payment_schedule) {
    if (payments_array.includes(frm.doc.payment_schedule[idx].payment_term)) {
      for (field of frm.fields_dict.payment_schedule.grid.grid_rows[idx].docfields) {
        frm.fields_dict.payment_schedule.grid.grid_rows[idx].toggle_editable(field.fieldname, false);
      }
      frm.fields_dict.payment_schedule.grid.refresh();
    }
  }
}