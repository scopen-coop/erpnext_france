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
  frm.add_custom_button(
    __("Down Payment Invoice"),
    () => {
      display_dialog_create_down_payment_invoice(frm);
    },
    __("Create")
  );
  //  await prevent_term_modification_if_payment_exist(frm)
});

frappe.ui.form.on("Sales Order", {
  delivery_date: function (frm) {
    frm.trigger("payment_terms_template");
  },
  transaction_date: function (frm) {
    frm.trigger("payment_terms_template");
  },
});

async function prevent_term_modification_if_payment_exist(frm) {
  let payments = await frappe.db.get_list("Payment Entry Reference", {
    fields: ["parent", "payment_term", "allocated_amount"],
    filters: {
      reference_doctype: "Sales Order",
      reference_name: frm.doc.name,
    },
  });

  let payments_array = payments.map((payment) => payment.payment_term);
  for (let idx in frm.doc.payment_schedule) {
    if (payments_array.includes(frm.doc.payment_schedule[idx].payment_term)) {
      for (let field of frm.fields_dict.payment_schedule.grid.grid_rows[idx]
        .docfields) {
        frm.fields_dict.payment_schedule.grid.grid_rows[idx].toggle_editable(
          field.fieldname,
          false
        );
      }
      frm.fields_dict.payment_schedule.grid.refresh();
    }
  }
}

const display_dialog_create_down_payment_invoice = function (frm) {
  let d = new frappe.ui.Dialog({
    title: "Enter details",
    fields: [
      {
        label: __("Down Payment Type"),
        fieldname: "down_payment_type",
        fieldtype: "Select",
        options: "ByAmount\nByPercent",
        reqd: 1,
      },
      {
        label: __("Down Payment Value"),
        fieldname: "down_payment_value",
        fieldtype: "Currency",
        reqd: 1,
      },
    ],
    size: "small", // small, large, extra-large
    primary_action_label: __("Create Down Payment"),
    async primary_action(values) {
      await init_document(frm, values);
      d.hide();
    },
  });

  d.show();
};

async function init_document(frm, values) {
  try {
    const response = await frappe.call({
      method:
        "erpnext_france.controllers.down_payment_invoice.init_down_payment_invoice",
      freeze: true,
      args: {
        order_name: frm.doc.name,
        values: values,
      },
    });

    if (response.message) {
      let new_doc_name = response.message;
      frappe.set_route("Form", "Sales Invoice", new_doc_name);
    }
  } catch (error) {
    frappe.msgprint({
      title: __("Error"),
      indicator: "red",
      message: __("An error occurred while initializing the document."),
    });
  }
}
