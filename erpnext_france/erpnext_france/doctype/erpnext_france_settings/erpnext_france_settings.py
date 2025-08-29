# -*- coding: utf-8 -*-
# Copyright (c) 2021, Britlog and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class ERPNextFranceSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		api_token: DF.Data | None
		api_url: DF.Data | None
		tva_accounting_on_down_payment: DF.Check
		update_item_supplier_part_no: DF.Check
	# end: auto-generated types
	pass
