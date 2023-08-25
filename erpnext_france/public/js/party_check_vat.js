frappe.ui.form.on("Customer", {
  custom_check_vat_id(frm) {
    frappe.call({
        method: "erpnext_france.check_vat.eu_vat.check_vat",
        args: {vat_id: frm.doc.tax_id},
        callback: function (r) {
          if (r.message)
            if (r.message.valid) {
                frappe.msgprint({
                    title: __('VAT Check OK'),
                    indicator: 'green',
                    message: __('Name: {0}, Adress:{1}',[r.message.name,r.message.address])
                });
            } else {
                frappe.msgprint({
                    title: __('Invalid VAT number'),
                    indicator: 'red',
                    message: __('Invalid VAT number')
                });
            }
        }
      })
  },
});

