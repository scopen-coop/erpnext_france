# Copyright (c) 2026, Scopen and contributors
# For license information, please see license.txt

from erpnext_france.dashboard.sepa_bordereau import add_sepa_bordereau_connection_for_payment_entry


def get_dashboard_data(data):
	return add_sepa_bordereau_connection_for_payment_entry(data)
