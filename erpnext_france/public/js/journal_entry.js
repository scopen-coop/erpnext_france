// Copyright (c) 2017, Britlog and contributors
// For license information, please see license.txt

frappe.ui.form.on("Journal Entry", "is_opening", function(frm,cdt,cdn) {

    //frappe.msgprint(frm.doc.is_opening);

    if (frm.doc.is_opening == "Yes") {
        frm.set_value("naming_series", "ANO-");
    } else {
        frm.set_value("naming_series", "OD-");
    }

});