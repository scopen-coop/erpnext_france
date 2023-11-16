// Copyright (c) 2019, Dokos SAS and Contributors
// For license information, please see license.txt

frappe.provide("erpnext.accounts");

frappe.pages['bank-reconciliation'].on_page_load = function(wrapper) {
	frappe.require('bank_reconciliation.bundle.js', function() {
		new erpnext.accounts.bankReconciliationPage(wrapper);
	});
}
