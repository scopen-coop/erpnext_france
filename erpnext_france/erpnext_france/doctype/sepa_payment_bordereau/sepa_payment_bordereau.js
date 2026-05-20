// Copyright (c) 2026, Scopen and contributors
// For license information, please see license.txt

function company_bank_account_filters(company) {
	return {
		company: company,
		is_company_account: 1
	};
}

function set_default_bank_account(frm) {
	if (!frm.doc.company || frm.doc.bank_account) {
		return;
	}

	frappe.db.get_value('Company', frm.doc.company, 'default_bank_account', function(company) {
		const filters = company_bank_account_filters(frm.doc.company);

		if (company && company.default_bank_account) {
			frappe.db.get_value(
				'Bank Account',
				{ ...filters, account: company.default_bank_account },
				'name',
				function(r) {
					if (r && r.name) {
						frm.set_value('bank_account', r.name);
					} else {
						set_fallback_company_bank_account(frm, filters);
					}
				}
			);
		} else {
			set_fallback_company_bank_account(frm, filters);
		}
	});
}

function set_fallback_company_bank_account(frm, filters) {
	frappe.db.get_value(
		'Bank Account',
		{ ...filters, is_default: 1 },
		'name',
		function(r) {
			if (r && r.name) {
				frm.set_value('bank_account', r.name);
			}
		}
	);
}

function ensure_company_bank_account(frm) {
	if (!frm.doc.bank_account || !frm.doc.company) {
		return;
	}

	frappe.db.get_value('Bank Account', frm.doc.bank_account, 'is_company_account', function(r) {
		if (r && !r.is_company_account) {
			frm.set_value('bank_account', null);
			set_default_bank_account(frm);
			frappe.show_alert({
				message: __('Customer/supplier bank account replaced with company bank account'),
				indicator: 'orange'
			});
		}
	});
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

		// Add Download SEPA File button when a file is already generated
		if (frm.doc.sepa_file) {
			frm.add_custom_button(__('Download SEPA File'), function() {
				const download_url = `/api/method/frappe.utils.file_manager.download_file?file_url=${encodeURIComponent(frm.doc.sepa_file)}`;
				window.location.href = download_url;
			});
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
		frm.trigger('setup_bank_account_query');
		if (frm.doc.bank_account) {
			ensure_company_bank_account(frm);
		} else {
			set_default_bank_account(frm);
		}
	},

	company: function(frm) {
		frm.set_value('bank_account', null);
		frm.trigger('setup_bank_account_query');
		set_default_bank_account(frm);
	},

	setup_bank_account_query: function(frm) {
		if (!frm.doc.company) {
			return;
		}

		frm.set_query('bank_account', function() {
			return {
				filters: company_bank_account_filters(frm.doc.company)
			};
		});
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
