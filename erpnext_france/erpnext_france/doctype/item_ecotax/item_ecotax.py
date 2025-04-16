# Copyright (c) 2025, Scopen and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ItemEcoTax(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		buy_account: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		sell_account: DF.Link | None
		tax_type: DF.Literal["DEEE", "PMCB"]
	# end: auto-generated types
	pass
