import erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts

import erpnext_france.regional.france.chart_of_accounts.chart_of_accounts
__version__ = "15.0.2"

#
# Monkey patch for chart of account
#

erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts.get_chart = (
	erpnext_france.regional.france.chart_of_accounts.chart_of_accounts.get_charts_for_fr
)

