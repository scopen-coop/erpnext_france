# Copyright (c) 2025, Scopen and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class PaymentTermsTemplateDetailBeforeInvoice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		credit_days: DF.Int
		date_computed_based_on: DF.Literal["Document Date", "Delivery Date"]
		description: DF.SmallText | None
		invoice_portion: DF.Float
		mode_of_payment: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		payment_term: DF.Link
		payment_terms_before_invoice: DF.Check
	# end: auto-generated types
	pass
