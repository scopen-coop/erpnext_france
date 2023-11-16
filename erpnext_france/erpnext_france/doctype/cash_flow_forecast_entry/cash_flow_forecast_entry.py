# Copyright (c) 2023, Dokos SAS and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CashFlowForecastEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		category: DF.Literal["Inflow", "Outflow"]
		date: DF.Date
		description: DF.SmallText
		repeat: DF.Literal["", "Weekly", "Monthly", "Quarterly", "Yearly"]
		repeat_end_date: DF.Date | None
		scenario: DF.Link | None
	# end: auto-generated types
	pass
