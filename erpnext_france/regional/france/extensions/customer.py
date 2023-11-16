from erpnext_france.regional.france.extensions.supplier import (
	get_info_from_pappers,
	get_siren_from_tax_id,
)


def validate(doc, method):
	get_siren_from_tax_id(doc)
	get_info_from_pappers(doc)
