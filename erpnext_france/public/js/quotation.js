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
  onload: function(frm) {
    // Vérifiez que TransactionController est chargé
    if (erpnext.TransactionController) {
      // Instanciation de la classe et assignation à une propriété du formulaire
      frm.transaction_controller = new erpnext.TransactionController({ frm: frm });
    }
  },
	payment_terms_template(frm) {
		const doc = frm.doc;
		if(doc.payment_terms_template && doc.doctype !== 'Delivery Note' && !doc.is_return) {
			var posting_date = doc.posting_date || doc.transaction_date;
			frappe.call({
				method: "erpnext_france.controllers.party.get_payment_terms_before_invoice",
				args: {
					terms_template: doc.payment_terms_template,
					posting_date: posting_date,
					grand_total: doc.rounded_total || doc.grand_total,
					base_grand_total: doc.base_rounded_total || doc.base_grand_total,
					delivery_date: doc.bill_date
				},
				callback: function(r) {
					if(r.message && !r.exc) {
						frm.set_value("payment_schedule", r.message);
						const company_currency = frm.transaction_controller.get_company_currency();
						frm.transaction_controller.update_payment_schedule_grid_labels(company_currency);
					}
				}
			})
		}
	}
});
