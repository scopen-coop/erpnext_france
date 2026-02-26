// Copyright (c) 2026, Scopen and contributors
// For license information, please see license.txt

function set_default_bank_account(frm) {
	if (frm.doc.company && !frm.doc.bank_account) {
		frappe.db.get_value('Company', frm.doc.company, 'default_bank_account', function(company) {
			if (company && company.default_bank_account) {
				frappe.db.get_value('Bank Account',
					{'company': frm.doc.company, 'account': company.default_bank_account},
					'name',
					function(r) {
						if (r && r.name) {
							frm.set_value('bank_account', r.name);
						} else {
							frappe.db.get_value('Bank Account',
								{'company': frm.doc.company, 'is_default': 1},
								'name',
								function(fallback) {
									if (fallback && fallback.name) {
										frm.set_value('bank_account', fallback.name);
									}
								}
							);
						}
					}
				);
			} else {
				frappe.db.get_value('Bank Account',
					{'company': frm.doc.company, 'is_default': 1},
					'name',
					function(r) {
						if (r && r.name) {
							frm.set_value('bank_account', r.name);
						}
					}
				);
			}
		});
	}
}

frappe.ui.form.on('SEPA Payment Bordereau', {
	refresh: function(frm) {
		// Add Validate button
		if (frm.doc.status === 'Draft' && frm.doc.lines && frm.doc.lines.length > 0) {
			frm.add_custom_button(__('Validate Bordereau'), function() {
				frappe.call({
					method: 'validate_bordereau',
					doc: frm.doc,
					callback: function(r) {
						frm.reload_doc();
					}
				});
			}).addClass('btn-primary');
		}

		// Add Generate SEPA File button
		if (frm.doc.status === 'Validated' || frm.doc.status === 'Exported') {
			frm.add_custom_button(__('Generate SEPA File'), function() {
				frappe.call({
					method: 'generate_sepa_file',
					doc: frm.doc,
					callback: function(r) {
						if (r.message) {
							frappe.msgprint(__('SEPA file generated: {0}', [r.message]));
							frm.reload_doc();
						}
					}
				});
			}).addClass('btn-primary');
		}

		// Add Mark as Sent button
		if (frm.doc.status === 'Exported') {
			frm.add_custom_button(__('Mark as Sent'), function() {
				frappe.call({
					method: 'mark_as_sent',
					doc: frm.doc,
					callback: function(r) {
						frm.reload_doc();
					}
				});
			});
		}

		// Set color indicator based on status
		if (frm.doc.status) {
			var color_map = {
				'Draft': 'gray',
				'Validated': 'blue',
				'Exported': 'orange',
				'Sent': 'purple',
				'Partial Rejections': 'red',
				'Closed': 'green'
			};
			frm.page.set_indicator(frm.doc.status, color_map[frm.doc.status]);
		}
	},

	payment_type: function(frm) {
		// Update naming when payment type changes
		frm.trigger('set_naming');
	},

	onload: function(frm) {
		// Set query for bank account to only show company's bank accounts
		if (frm.doc.company) {
			frm.set_query('bank_account', function() {
				return {
					filters: {
						'company': frm.doc.company,
						'is_company_account': 1
					}
				};
			});
		}

		// Ensure default bank account is set on new bordereau
		set_default_bank_account(frm);
	},

	company: function(frm) {
		// Set default bank account when company changes
		set_default_bank_account(frm);
	}
});

frappe.ui.form.on('SEPA Payment Bordereau Line', {
	amount: function(frm) {
		// Recalculate total when line amount changes
		frm.trigger('calculate_total');
	},

	lines_remove: function(frm) {
		// Recalculate total when line is removed
		frm.trigger('calculate_total');
	}
});
