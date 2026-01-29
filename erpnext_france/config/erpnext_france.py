from frappe import _


def get_data():
	data = [
		{
			"label": _("Accounting"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Accounting Export",
					"label": _("Accounting Export"),
					"description": _("Export ledgers to your favorite accounting software."),
				}
			],
		},
		{
			"label": _("Setup"),
			"icon": "fa fa-cog",
			"items": [
				{
					"type": "doctype",
					"name": "ERPNext France Settings",
					"description": _("Default settings for ERPNext France."),
				}
			],
		},
	]

	return data
