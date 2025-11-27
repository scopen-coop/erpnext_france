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
		{
			"label": _("Special Item Accountancy Code Setup"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Categorie comptable Tiers",
					"label": _("Categorie comptable Tiers"),
					"description": _("Categorie comptable Tiers"),
				},
				{
					"type": "doctype",
					"name": "Special Item Accountancy Code Default",
					"label": _("Categorie comptable Tiers et code comptable Produit par défaut"),
					"description": _("Categorie comptable Tiers et code comptable Produit par défaut"),
				},
			],
		},
	]

	return data
