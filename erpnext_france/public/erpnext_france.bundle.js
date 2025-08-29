erpnext.TransactionController.prototype.payment_terms_template = async function(doc, doctype, docname) {
  if (erpnext.TransactionController) {
    // Instanciation de la classe et assignation à une propriété du formulaire
    this.frm.transaction_controller = new erpnext.TransactionController({ frm: this.frm });
  }

  me = this

  if(['Quotation', 'Sales Order'].includes(doctype) && doc.payment_terms_template) {
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


display_dialog_create_down_payment_item = function (frm, company) {
  let d = new frappe.ui.Dialog({
    title: 'Enter details',
    fields: [
      {
        label: __('Item Group'),
        fieldname: 'item_group',
        fieldtype: 'Link',
        options: 'Item Group',
        reqd: 1
      },
      {
        label: __('Income Account'),
        fieldname: 'income_account',
        fieldtype: 'Link',
        options: 'Account',
        filters: {
					root_type: "Income",
					is_group: 0,
					company: company,
				},
        reqd: 1
      },
      {
        label: __('Expense Account'),
        fieldname: 'expense_account',
        fieldtype: 'Link',
        options: 'Account',
        filters: {
					root_type: "Expense",
					is_group: 0,
					company: company,
				},
        reqd: 1
      }
    ],
    size: 'small', // small, large, extra-large
    primary_action_label: 'Submit',
    primary_action(values) {
      frm.call({
        method:
          "erpnext_france.utils.create_down_payment_item.create_down_payment_item",
        args: {
          company: company,
          item_group: values.item_group,
          income_account: values.income_account,
          expense_account: values.expense_account,
        },
        freeze: true,
        callback: function () {
          frappe.msgprint(
            __(
              "Down Payment Item Successfully created"
            )
          );
        },
      });
      d.hide();
    }
  });

  d.show();
};
