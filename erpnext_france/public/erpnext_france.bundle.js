erpnext.TransactionController.prototype.payment_terms_template = async function(doc, doctype, docname) {
  if (erpnext.TransactionController) {
    // Instanciation de la classe et assignation à une propriété du formulaire
    this.frm.transaction_controller = new erpnext.TransactionController({ frm: this.frm });
  }

  me = this
  if(doc.payment_terms_template && ['Quotation', 'Sales Order'].includes(doctype)) {
    get_payment_terms_before_invoice(
      me,
      doctype,
      doc.rounded_total || doc.grand_total,
      doc.base_rounded_total || doc.base_grand_total,
      doc.posting_date || doc.transaction_date,
      doc.delivery_date,
      doc.payment_terms_template
    );
  } else if (doctype == 'Sales Invoice') {
    let posting_date = null;
    if (doc.items.length > 0 && doc.items[0].sales_order) {
      let sales_order = doc.items[0].sales_order;
      frappe.call({
          method: 'frappe.client.get_value',
          args: {
          doctype: 'Sales Order',
          name: sales_order,
          fieldname: 'transaction_date'
        },
        callback: function(r) {
          let transaction_date = r.message.transaction_date
          if (transaction_date) {
            get_payment_terms_before_invoice(
              me,
              doctype,
              doc.rounded_total || doc.grand_total,
              doc.base_rounded_total || doc.base_grand_total,
              transaction_date,
              doc.posting_date,
              doc.payment_terms_template
            );
          }
        }
      });
    }
  } else {
    me.frm.transaction_controller.payment_terms_template();
  }
}


function get_payment_terms_before_invoice(me, doctype, grand_total, base_grand_total, posting_date, delivery_date, payment_terms_template) {

  frappe.call({
    method: "erpnext_france.controllers.party.get_payment_terms_before_invoice",
    args: {
      doctype: doctype,
      grand_total: grand_total,
      base_grand_total: base_grand_total,
      posting_date: posting_date,
      delivery_date: delivery_date,
      payment_terms_template: payment_terms_template
    },
    callback: function(r) {
      if(r.message && !r.exc) {
        me.frm.set_value("payment_schedule", r.message);
        const company_currency = me.frm.transaction_controller.get_company_currency();
        me.frm.transaction_controller.update_payment_schedule_grid_labels(company_currency);
      }
    }
  })
}