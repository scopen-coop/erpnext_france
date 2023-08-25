// Copyright (c) 2021, Britlog and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Order', {
  refresh: function (frm) {
    if (flt(frm.doc.per_billed, 6) < 100) {
      frm.add_custom_button(__('Deposit Invoice'), () => {
        frappe.prompt(
          {
            label: __('Payment Term'),
            fieldname: 'payment_term',
            fieldtype: 'Link',
            options: 'Payment Term',
            description: __('Select Payment Term'),
            get_query: () => {
              return {
                query: "erpnext_france.erpnext_france.deposit_invoice.deposit_invoice.get_payment_schedule_query",
                filters: {'parent': frm.doc.name}
              }
            }
          },
          (values) => {

            frappe.model.open_mapped_doc({
              method: "erpnext_france.erpnext_france.deposit_invoice.deposit_invoice.make_deposit_invoice",
              frm: frm,
              args: {payment_term: values.payment_term}
            })

          },
          __('Deposit Invoice')
        )
      }, __('Create'))
    }
  }
});
