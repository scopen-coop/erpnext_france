frappe.listview_settings['Adjustment Entry'] = {
	get_indicator: function(doc) {
		if(doc.status=="Reversed") {
			return [__("Reversed"), "green", "status,=,Reversed"]
		}
	}
}