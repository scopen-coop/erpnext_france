import frappe


def execute():
	frappe.db.sql(
		"""
        UPDATE `tabPayment Term`
        SET `custom_due_date_based_on_france` = `due_date_based_on`
        WHERE (`custom_due_date_based_on_france` IS NULL
            OR `custom_due_date_based_on_france` = '')
        AND (`due_date_based_on` IS NOT NULL
            AND `due_date_based_on` != '')
    """
	)
