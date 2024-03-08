// Copyright (c) 2023, scopen.fr and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer", {
	check_vat_id(frm) {
		frappe.call({
			method: "erpnext_france.utils.eu_vat.check_vat",
			args: {vat_id: frm.doc.tax_id},
			freeze: true,
			freeze_message: __('Check request sent to EU web site, please wait'),
			callback: function (r) {
				if (r.message)
					if (r.message.valid) {
						frappe.msgprint({
							title: __('VAT Check OK'),
							indicator: 'green',
							as_list: true,
							message: [__('Name: {0}', [r.message.name]), __('Adress: {0}', [r.message.address]), __('Source: https://ec.europa.eu/taxation_customs/vies/#/vat-validation')]
						});
					} else {
						frappe.msgprint({
							title: __('Invalid VAT number'),
							indicator: 'red',
							as_list: true,
							message: [__('Invalid VAT number'), __('Source: https://ec.europa.eu/taxation_customs/vies/#/vat-validation')]
						});
					}
			}
		});
	},
});


frappe.ui.form.on("Supplier", {
	check_vat_id(frm) {
		frappe.call({
			method: "erpnext_france.utils.eu_vat.check_vat",
			args: {vat_id: frm.doc.tax_id},
			freeze: true,
			freeze_message: __('Check request sent to EU web site, please wait'),
			callback: function (r) {
				if (r.message)
					if (r.message.valid) {
						frappe.msgprint({
							title: __('VAT Check OK'),
							indicator: 'green',
							as_list: true,
							message: [__('Name: {0}', [r.message.name]),
								__('Adress: {0}', [r.message.address]),
								__('Source:https://ec.europa.eu/taxation_customs/vies/#/vat-validation')]
						});
					} else {
						frappe.msgprint({
							title: __('Invalid VAT number'),
							indicator: 'red',
							as_list: true,
							message: [__('Invalid VAT number'), __('Source:https://ec.europa.eu/taxation_customs/vies/#/vat-validation')]
						});
					}
			}
		})
	},
});
