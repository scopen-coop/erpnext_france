erpnext.TransactionController.prototype.payment_terms_template = function(doc, doctype, docname) {
  if (erpnext.TransactionController) {
    // Instanciation de la classe et assignation à une propriété du formulaire
    this.frm.transaction_controller = new erpnext.TransactionController({ frm: this.frm });
  }

  me = this
  if(doc.payment_terms_template && ['Quotation', 'Sales Order', 'Sales Invoice'].includes(doctype)) {
    frappe.call({
      method: "erpnext_france.controllers.party.get_payment_terms_before_invoice",
      args: {
        doctype: doctype,
        grand_total: doc.rounded_total || doc.grand_total,
        base_grand_total: doc.base_rounded_total || doc.base_grand_total,
        posting_date: doc.posting_date || doc.transaction_date,
        delivery_date: doc.delivery_date,
        payment_terms_template: doc.payment_terms_template
      },
      callback: function(r) {
        if(r.message && !r.exc) {
          me.frm.set_value("payment_schedule", r.message);
          const company_currency = me.frm.transaction_controller.get_company_currency();
          me.frm.transaction_controller.update_payment_schedule_grid_labels(company_currency);
        }
      }
    })
  } else {
    me.frm.transaction_controller.payment_terms_template();
  }
}