// Copyright (c) 2017, Britlog and contributors
// For license information, please see license.txt

//Now FEC export is core module I do not remove all the code, but it should be
// frappe.ui.form.on("Payment Entry", "mode_of_payment", function(frm,cdt,cdn) {
//
//     //frappe.msgprint(frm.doc.mode_of_payment);
//
//     frappe.call({
//         method: "erpnext_france.fec.journal.get_journal_code",
//         args: {
//             "mode_of_payment": frm.doc.mode_of_payment,
//             "company": frm.doc.company
//         },
//         callback: function(r) {
//             //console.log(r.message);
//             if (r.message) {
//               frm.set_value("naming_series", r.message+"-");
//             }
//         }
//     });
// });
