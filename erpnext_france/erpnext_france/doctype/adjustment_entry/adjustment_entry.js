// Copyright (c) 2021, Dokos SAS and contributors
// Copyright (c) 2023, Scopen and contributors
// For license information, please see license.txt

frappe.ui.form.on('Adjustment Entry', {
	refresh(frm) {
		if(frm.doc.docstatus > 0) {
			frm.add_custom_button(__('Ledger'), function() {
				frappe.route_options = {
					"voucher_no": frm.doc.name,
					"from_date": frm.doc.posting_date,
					"to_date": frappe.datetime.nowdate(),
					"company": frm.doc.company,
					"group_by": ""
				};
				frappe.set_route("query-report", "General Ledger");
			}, "fas fa-table");
		}
	},
	get_documents(frm) {
		frappe.call({
			method: "erpnext.accounts.doctype.adjustment_entry.adjustment_entry.get_documents",
			args: {
				entry_type: frm.doc.entry_type,
				date: frm.doc.posting_date,
				company: frm.doc.company
			}
		}).then(r => {
			frm.clear_table('details')
			r.message.documents.forEach((d) => {
				frm.add_child("details",d);
			});
			frm.refresh_field("details");

			frm.set_value("total_debit", r.message.total_debit);
			frm.refresh_field("total_debit");
			frm.set_value("total_credit", r.message.total_credit);
			frm.refresh_field("total_credit");
			frm.set_value("total_posting_amount", r.message.total_posting_amount);
			frm.refresh_field("total_posting_amount");
		})
	}
});

frappe.tour["Adjustment Entry"] = {
	"fr": [
		{
			fieldname: "entry_type",
			description: "Sélectionnez <strong>Revenus différés</strong> pour comptabiliser les revenus constatés d'avance ou <strong>Charges différées</strong> pour les charges constatées d'avance."
		},
		{
			fieldname: "adjustment_account",
			description: "Sélectionnez le compte comptable à utiliser pour constater le revenu ou la charge constatée d'avance.<br>Pour les revenus ce sera probablement une subdivision du compte 487, pour le charges une subdivision du compte 486."
		},
		{
			fieldname: "posting_date",
			description: "Sélectionnez la date de comptabilisation de l'écriture. Ce sera probablement le dernier jour de l'exercice fiscal concerné."
		},
		{
			fieldname: "reversal_date",
			description: "Sélectionnez la date d'annulation/extourne de l'écriture. Ce sera probablement le premier jour de l'exercice fiscal suivant."
		},
		{
			fieldname: "get_documents",
			description: "En cliquant sur ce bouton Dokos récupère toutes les factures contenant des prestations courant sur deux exercices grâce aux dates de début et de fin de la section <strong>Abonnement</strong>.<br>Le montant à comptabiliser est calculé pro-rata temporis."
		},
	]
}