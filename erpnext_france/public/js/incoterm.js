// Copyright (c) 2025, scopen.fr and contributors
// For license information, please see license.txt

const INCOTERM_DOCTYPE_CONFIG = {
  "Sales Order": "customer",
  "Sales Invoice": "customer",
  // "Purchase Invoice": "supplier",
  // "Delivery Note": "customer",
  // "Purchase Order": "supplier",
  // "Purchase Receipt": "supplier",
};

// Fonction générique
function set_incoterm_from_party(frm, party_field) {
  console.log("set_incoterm_from_party");
  const party = frm.doc[party_field];

  if (!party) return;

  const party_doctype = party_field === "customer" ? "Customer" : "Supplier";

  frappe.db.get_value(party_doctype, party, "incoterm", function (value) {
    const incoterm = value && value.incoterm;

    if (!incoterm) return;

    frm.set_value("incoterm", incoterm);
  });
}

// Génération automatique des handlers depuis le dict
Object.entries(INCOTERM_DOCTYPE_CONFIG).forEach(([doctype, party_field]) => {
  if (!party_field) return;

  frappe.ui.form.on(doctype, {
    [party_field]: function (frm) {
      set_incoterm_from_party(frm, party_field);
    },
  });
});
