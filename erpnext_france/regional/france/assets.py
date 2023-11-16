from frappe.utils import add_months, cint, date_diff, flt, get_last_day, getdate


def get_depreciation_amount(asset, depreciable_value, row, *args, **kwargs):
	if row.depreciation_method in ("Straight Line", "Manual"):
		# if the Depreciation Schedule is being prepared for the first time
		if not asset.flags.increase_in_asset_life:
			depreciation_amount = (
				flt(asset.gross_purchase_amount) - flt(row.expected_value_after_useful_life)
			) / flt(row.total_number_of_depreciations)

		# if the Depreciation Schedule is being modified after Asset Repair
		else:
			depreciation_amount = (
				flt(row.value_after_depreciation) - flt(row.expected_value_after_useful_life)
			) / (date_diff(asset.to_date, asset.available_for_use_date) / 365)
	else:
		depreciation_amount = flt(depreciable_value * (flt(row.rate_of_depreciation) / 100))

	return depreciation_amount


def get_total_days(date, frequency):
	period_start_date = add_months(date, cint(frequency) * -1)
	if is_last_day_of_the_month(date):
		period_start_date = get_last_day(period_start_date)

	return min(date_diff(date, period_start_date), 360)


def is_last_day_of_the_month(date):
	last_day_of_the_month = get_last_day(date)

	return getdate(last_day_of_the_month) == getdate(date)


def date_difference(to_date, from_date):
	"""
	Calculate a difference based on a 30 days per months rule
	"""
	day = getdate(from_date).day
	month = getdate(from_date).month

	if (month == 2 and day >= 28) or day > 30:
		day = 30

	first_month_diff = 30 - day

	return 30 * (getdate(to_date).month - month) + first_month_diff
