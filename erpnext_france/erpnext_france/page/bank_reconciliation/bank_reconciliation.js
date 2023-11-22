// Copyright (c) 2019, Dokos SAS and Contributors
// For license information, please see license.txt


frappe.pages['bank-reconciliation'].on_page_load = function(wrapper) {
	frappe.require('assets/erpnext_france/js/bank_reconciliation.js', function() {
		new BankReconciliationPage(wrapper);
	});
}
