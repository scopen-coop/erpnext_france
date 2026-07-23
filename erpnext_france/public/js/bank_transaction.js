frappe.ui.form.on("Bank Transaction", {
  refresh: function (frm) {
    if (frm.doc.docstatus === 1 && frm.doc.unallocated_amount > 0) {
      frm.add_custom_button(
        __("Reconcile SEPA"),
        function () {
          frappe.prompt(
            [
              {
                label: __("End-to-End ID"),
                fieldname: "end_to_end_id",
                fieldtype: "Data",
                reqd: 1,
              },
            ],
            (values) => {
              frappe.call({
                method:
                  "erpnext_france.regional.france.sepa_utils.reconcile_bank_transaction_to_sepa_line",
                args: {
                  bank_transaction: frm.doc.name,
                  end_to_end_id: values.end_to_end_id,
                },
                callback: function (r) {
                  if (!r.exc) {
                    frm.reload_doc();
                  }
                },
              });
            },
            __("Enter SEPA Details"),
            __("Reconcile")
          );
        },
        __("Actions")
      );
    }
  },
});
