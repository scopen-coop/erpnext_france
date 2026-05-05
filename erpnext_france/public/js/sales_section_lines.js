// Copyright (c) 2026, Scopen and contributors
// Gestion des lignes "titre de section" et "sous-total" dans les documents
// Quotation, Sales Order, Sales Invoice et Delivery Note.

const SALES_DOCTYPES = ["Quotation", "Sales Order", "Sales Invoice", "Delivery Note"];
const SALES_ITEM_DOCTYPES = [
  "Quotation Item",
  "Sales Order Item",
  "Sales Invoice Item",
  "Delivery Note Item",
];
const SECTION_TYPES = ["Section Header", "Subtotal"];

// Injection unique des styles CSS pour la mise en evidence visuelle des lignes
function inject_section_styles() {
  if (document.getElementById("ef-section-styles")) return;
  const style = document.createElement("style");
  style.id = "ef-section-styles";
  style.textContent = `
    .grid-row.ef-section-row .grid-static-col,
    .grid-row.ef-section-row .data-row { background-color: #e3eaf3 !important; font-weight: 600; }
    .grid-row.ef-subtotal-row .grid-static-col,
    .grid-row.ef-subtotal-row .data-row { background-color: #fcf3cf !important; font-weight: 600; }
  `;
  document.head.appendChild(style);
}

// Calcule ef_section_amount sur les lignes Subtotal cote client (miroir du serveur)
function recompute_subtotals(frm) {
  let running = 0;
  (frm.doc.items || []).forEach((item) => {
    const t = item.ef_line_type || "Item";
    if (t === "Section Header") {
      running = 0;
      item.ef_section_amount = 0;
    } else if (t === "Subtotal") {
      item.ef_section_amount = running;
    } else {
      running += flt(item.amount);
    }
  });
  frm.refresh_field("items");
}

// Met en evidence les lignes Section Header / Subtotal dans la grille
function apply_section_styles(frm) {
  const grid = frm.fields_dict.items && frm.fields_dict.items.grid;
  if (!grid || !grid.grid_rows_by_docname) return;
  (frm.doc.items || []).forEach((item) => {
    const row = grid.grid_rows_by_docname[item.name];
    if (!row || !row.row) return;
    const $row = $(row.row);
    $row.removeClass("ef-section-row ef-subtotal-row");
    if (item.ef_line_type === "Section Header") $row.addClass("ef-section-row");
    else if (item.ef_line_type === "Subtotal") $row.addClass("ef-subtotal-row");
  });
}

// Boutons d'ajout dans la grille
function setup_section_buttons(frm) {
  const grid = frm.fields_dict.items && frm.fields_dict.items.grid;
  if (!grid) return;

  const add_button = (label, line_type) => {
    grid.add_custom_button(__(label), () => {
      const row = frm.add_child("items", {
        ef_line_type: line_type,
        qty: 0,
        rate: 0,
        amount: 0,
      });
      // Le item_code est non-requis sur ces lignes (cf. property setters)
      frm.refresh_field("items");
      recompute_subtotals(frm);
      apply_section_styles(frm);
    });
  };

  // add_custom_button est idempotent (Frappe verifie l'existence)
  add_button("Ajouter un titre de section", "Section Header");
  add_button("Ajouter un sous-total", "Subtotal");
}

// Force qty/rate/amount a 0 quand l'utilisateur passe une ligne en Section/Subtotal
function on_line_type_change(frm, cdt, cdn) {
  const row = locals[cdt][cdn];
  if (SECTION_TYPES.includes(row.ef_line_type)) {
    row.qty = 0;
    row.rate = 0;
    row.amount = 0;
    frm.refresh_field("items");
  }
  recompute_subtotals(frm);
  apply_section_styles(frm);
}

// Branchement sur les 4 doctypes parents
SALES_DOCTYPES.forEach((dt) => {
  frappe.ui.form.on(dt, {
    setup: inject_section_styles,
    refresh(frm) {
      inject_section_styles();
      setup_section_buttons(frm);
      apply_section_styles(frm);
    },
    items_add(frm) {
      recompute_subtotals(frm);
      apply_section_styles(frm);
    },
    items_remove(frm) {
      recompute_subtotals(frm);
      apply_section_styles(frm);
    },
  });
});

// Branchement sur les 4 child doctypes
SALES_ITEM_DOCTYPES.forEach((cdt_name) => {
  frappe.ui.form.on(cdt_name, {
    ef_line_type: on_line_type_change,
    amount(frm) {
      recompute_subtotals(frm);
    },
    qty(frm) {
      recompute_subtotals(frm);
    },
    rate(frm) {
      recompute_subtotals(frm);
    },
  });
});
