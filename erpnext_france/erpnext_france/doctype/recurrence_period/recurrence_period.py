# Copyright (c) 2023, Dokos SAS and contributors
# Copyright (c) 2023, Scopen and contributors
# For license information, please see license.txt

from calendar import monthrange

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_to_date, cint, get_first_day, get_last_day, getdate, nowdate


class RecurrencePeriod(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		billing_interval: DF.Link | None
		billing_interval_count: DF.Int
		generate_invoice_at_period_start: DF.Check
		generate_invoice_before_payment: DF.Check
		periodicity: DF.Literal["Day", "Week", "Month", "Year"]
		start_date: DF.Literal[
			"Delivery date", "1st day of the month", "15th day of the month", "Last day of the month"
		]
		title: DF.Data | None
	# end: auto-generated types
	def validate(self):
		self.validate_interval_count()

	def validate_interval_count(self):
		if self.billing_interval_count < 1:
			frappe.throw(_("Billing Interval Count cannot be less than 1"))

	def get_start_date(self, start=None):
		if not start:
			start = getdate(nowdate())

		if self.start_date == "1st day of the month":
			return get_first_day(start)
		elif self.start_date == "15th day of the month":
			return getdate(start).replace(day=1)
		elif self.start_date == "Last day of the month":
			return get_last_day(start)

		return start

	def get_end_date(self, start=None, invoicing_day=None):
		start = getdate(start or nowdate())

		if not invoicing_day:
			invoicing_day = start.day

		if billing_cycle_data := self.get_billing_cycle_data():
			period_end = getdate(add_to_date(start, **billing_cycle_data))

			if self.periodicity in ("Month", "Year") and cint(invoicing_day) in [28, 29, 30, 31, 1]:
				month_max_no_of_days = monthrange(period_end.year, period_end.month)[1]
				if invoicing_day == 1:
					period_end = get_last_day(period_end)
				else:
					day = invoicing_day - 1 if month_max_no_of_days > invoicing_day else month_max_no_of_days - 1
					period_end = period_end.replace(day=day)

			return period_end

		return get_last_day(start)

	def get_billing_cycle_data(self):
		data = {}
		interval = self.periodicity
		interval_count = self.billing_interval_count
		if interval not in ["Day", "Week"]:
			data["days"] = -1
		if interval == "Day":
			data["days"] = interval_count - 1
		elif interval == "Month":
			data["months"] = interval_count
		elif interval == "Year":
			data["years"] = interval_count
		elif interval == "Week":
			data["days"] = interval_count * 7 - 1

		return data
