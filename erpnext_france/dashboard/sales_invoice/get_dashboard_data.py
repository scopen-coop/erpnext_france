# Copyright (c) 2026, Scopen and contributors
# For license information, please see license.txt

from erpnext_france.dashboard.sepa_bordereau import add_sepa_bordereau_connection


def get_dashboard_data(data):
	return add_sepa_bordereau_connection(data, "Sales Invoice")
