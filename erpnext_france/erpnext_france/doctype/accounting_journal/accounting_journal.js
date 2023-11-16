// Copyright (c) 2019, Dokos SAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Accounting Journal', {
	setup: function(frm) {
		frm.set_query("account", function() {
			return {
				filters: {
					'account_type': frm.doc.type,
					'company': frm.doc.company,
					'is_group': 0
				}
			};
		});
	}
});


frappe.tour['Accounting Journal'] = [
	{
		fieldname: "journal_name",
		title: __("Journal name"),
		description: __("This is the label of this journal. It should be more explicit than the journal code."),
	},
	{
		fieldname: "journal_code",
		title: __("Journal code"),
		description: __("This is the code of the journal. It will be displayed in the general ledger."),
	},
	{
		fieldname: "type",
		title: __("Journal type"),
		description: __("Can be used in transactions to filter journal codes."),
	},
	{
		fieldname: "account",
		title: __("Linked account"),
		description: __("If the journal is a bank or cash journal, it should be linked to the corresponding bank or cash account."),
	},
	{
		fieldname: "disabled",
		title: __("Enable/disable this journal"),
		description: __("If the journal is disabled, it will not be used anymore."),
	},
	{
		fieldname: "conditions",
		title: __("Link it to a transaction"),
		description: __("You can link your journal with specific transactions and add some conditions. E.g: Link it to a sales invoice with a condition `doc.is_return` for a credit notes journal."),
	}
]