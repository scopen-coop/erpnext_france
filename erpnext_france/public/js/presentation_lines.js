// Copyright (c) 2026, Scopen and contributors
// For license information, please see license.txt

const PRESENTATION_PARENTS = ["Quotation", "Sales Order", "Sales Invoice"];
const PRESENTATION_CHILDREN = ["Quotation Item", "Sales Order Item", "Sales Invoice Item"];

function add_presentation_buttons(frm) {
  if (frm.doc.docstatus !== 0) return;

  const group = __("Add Presentation Line");

  frm.add_custom_button(
    __("Section"),
    () => prompt_and_add(frm, "Section"),
    group
  );
  frm.add_custom_button(
    __("Note"),
    () => prompt_and_add(frm, "Note"),
    group
  );
  frm.add_custom_button(
    __("Subtotal"),
    () => add_presentation_row(frm, "Subtotal"),
    group
  );
}

function prompt_and_add(frm, display_type) {
  const d = new frappe.ui.Dialog({
    title: __("Add {0}", [__(display_type)]),
    fields: [
      {
        fieldname: "label",
        fieldtype: display_type === "Note" ? "Small Text" : "Data",
        label: __("Label"),
        reqd: 1,
      },
    ],
    primary_action_label: __("Add"),
    primary_action(values) {
      add_presentation_row(frm, display_type, values.label);
      d.hide();
    },
  });
  d.show();
}

function add_presentation_row(frm, display_type, label) {
  const row = frm.add_child("items");

  row.is_presentation_line = 1;
  row.display_type = display_type;
  if (label) {
    row.section_label = label;
    row.item_name = label;
    row.description = label;
  } else {
    row.item_name = display_type;
    row.description = display_type;
  }

  row.item_code = "";
  row.uom = "";
  row.stock_uom = "";
  row.conversion_factor = 1;

  // Force everything that drives totals to 0
  [
    "qty",
    "stock_qty",
    "rate",
    "amount",
    "net_amount",
    "net_rate",
    "base_rate",
    "base_amount",
    "base_net_amount",
    "base_net_rate",
    "price_list_rate",
    "base_price_list_rate",
    "discount_amount",
    "discount_percentage",
    "margin_rate_or_amount",
  ].forEach((f) => {
    if (f in row) row[f] = 0;
  });
  row.qty = 1;
  row.stock_qty = 1;

  frm.refresh_field("items");
  frm.dirty();
}

function on_row_flag_changed(frm, cdt, cdn) {
  const row = locals[cdt][cdn];
  if (!row.is_presentation_line) return;

  [
    "item_code",
    "uom",
    "stock_uom",
    "qty",
    "stock_qty",
    "rate",
    "amount",
    "net_amount",
    "discount_amount",
    "discount_percentage",
    "price_list_rate",
    "conversion_factor",
  ].forEach((f) => {
    if (f in row) {
      row[f] = ["item_code", "uom", "stock_uom"].includes(f) ? "" : 0;
    }
  });
  row.qty = 1;
  row.stock_qty = 1;
  row.conversion_factor = 1;
  frm.refresh_field("items");
}

PRESENTATION_PARENTS.forEach((dt) => {
  frappe.ui.form.on(dt, {
    refresh: add_presentation_buttons,
  });
});

PRESENTATION_CHILDREN.forEach((cdt) => {
  frappe.ui.form.on(cdt, {
    is_presentation_line: on_row_flag_changed,
    display_type: on_row_flag_changed,
  });
});
