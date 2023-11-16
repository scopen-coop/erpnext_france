frappe.listview_settings['Sepa Mandate'] = {
	get_indicator: function(doc) {
		if (doc.status == "Pending customer approval") {
			return [__("Pending customer approval"), "orange", "status,=,Pending customer approval"];
		} else if (doc.status == "Expired") {
			return [__("Expired"), "gray", "status,=,Expired"];
		} else if (doc.status == "Cancelled") {
			return [__("Cancelled"), "red", "status,=,Cancelled"];
		} else if (doc.status == "Failed") {
			return [__("Failed"), "red", "status,=,Failed"];
		} else if (doc.status == "Active") {
			return [__("Active"), "green", "status,=,Active"];
		} else if (doc.status == "Submitted") {
			return [__("Submitted"), "blue", "status,=,Submitted"];
		} else if (doc.status == "Pending submission") {
			return [__("Pending submission"), "orange", "status,=,Pending submission"];
		} else {
			return [__("Created"), "gray", "status,=,Created"];
		}
	},

	onload: function(listview) {
		listview.page.add_action_item(__("Purchase Order"), ()=>{
			erpnext.bulk_transaction_processing.create(listview, "Supplier Quotation", "Purchase Order");
		});

		listview.page.add_action_item(__("Purchase Invoice"), ()=>{
			erpnext.bulk_transaction_processing.create(listview, "Supplier Quotation", "Purchase Invoice");
		});
	}
};
