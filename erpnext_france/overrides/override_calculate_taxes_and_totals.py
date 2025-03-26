from erpnext.controllers import taxes_and_totals

class erpnext_france_calculate_taxes_and_totals(taxes_and_totals.calculate_taxes_and_totals):
    """Override for calculating taxes and totals in MyApp."""
    pass


taxes_and_totals.calculate_taxes_and_totals = erpnext_france_calculate_taxes_and_totals