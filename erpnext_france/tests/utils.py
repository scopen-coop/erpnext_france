# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from typing import Any, NewType

import frappe
from erpnext.setup.utils import set_defaults_for_tests
from frappe.core.doctype.report.report import get_report_module_dotted_path
from frappe.utils.data import now_datetime


def before_tests():
	frappe.clear_cache()
	# complete setup if missing
	from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

	if not frappe.db.a_row_exists("Company"):
		current_year = now_datetime().year
		setup_complete(
			{
				"currency": "EUR",
				"full_name": "Test User",
				"company_name": "Mon Plaisir Fruité",
				"timezone": "Europe/Paris",
				"company_abbr": "MPF",
				"industry": "Manufacturing",
				"country": "France",
				"fy_start_date": f"{current_year}-01-01",
				"fy_end_date": f"{current_year}-12-31",
				"language": "french",
				"company_tagline": "Testing",
				"email": "test@test.com",
				"password": "test",
				"chart_of_accounts": "France - Plan Comptable General 2025 avec code",
			}
		)

	frappe.db.sql("delete from `tabItem Price`")

	_enable_all_roles_for_admin()

	set_defaults_for_tests()

	frappe.db.commit()


def _enable_all_roles_for_admin():
	from frappe.desk.page.setup_wizard.setup_wizard import add_all_roles_to

	all_roles = set(frappe.db.get_values("Role", pluck="name"))
	admin_roles = set(
		frappe.db.get_values("Has Role", {"parent": "Administrator"}, fieldname="role", pluck="role")
	)

	if all_roles.difference(admin_roles):
		add_all_roles_to("Administrator")
