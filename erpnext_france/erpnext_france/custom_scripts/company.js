// Copyright (c) 2021, scopen.fr and contributors
// For license information, please see license.txt

frappe.ui.form.on("Company", {
        setup: function (frm) {
            frm.set_query('discount_supplier_account', function () {
                return {
                    filters: {
                        'root_type': 'Expense'
                    }
                }
            });
        }
    }
);
