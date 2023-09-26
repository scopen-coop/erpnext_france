// Copyright (c) 2021, scopen.fr and contributors
// For license information, please see license.txt


frappe.listview_settings["Customer"] = {
    onload(listview) {
        listview.page.add_inner_button(__('Import customer from SIRENE'),  import_thirdparty_from_sirene, '', 'primary')
    },
};

frappe.listview_settings["Supplier"] = {
    onload(listview) {
        listview.page.add_inner_button(__('Import supplier from SIRENE'),  import_thirdparty_from_sirene, '', 'primary')
    },
};

function import_thirdparty_from_sirene() {
    let dialog1 = new frappe.ui.Dialog({
        title: 'Enter entity details',
        fields: [
            {
                label: 'Company Name',
                fieldname: 'company_name',
                fieldtype: 'Data'
            },
            {
                label: 'SIREN',
                fieldname: 'siren',
                fieldtype: 'Data'
            },
            {
                label: 'SIRET',
                fieldname: 'siret',
                fieldtype: 'Data'
            },
            {
                label: 'NAF',
                fieldname: 'naf',
                fieldtype: 'Data'
            },
            {
                label: 'Zipcode',
                fieldname: 'zipcode',
                fieldtype: 'Data'
            },
            {
                label: 'Nb of displayed results',
                fieldname: 'nb_results',
                fieldtype: 'Int',
                default: 20
            },
        ],
        size: 'large', // small, large, extra-large
        primary_action_label: 'Submit',
        primary_action(data) {
            frappe.call({
                method: "erpnext_france.controllers.fetch_company_from_sirene.fetch_company_from_sirene",
                args: {data},
                callback: function (response) {
                    if (! response || ! response.message) {
                        frappe.throw(__('No Response From Server'));
                        return
                    }
                    
                    let dialog2 = new frappe.ui.Dialog({
                        title: 'Enter entity details',
                        fields: [
                            {
                                label: 'Company Name',
                                fieldname: 'company_name',
                                fieldtype: 'Data'
                            },
                        ],
                        size: 'large', // small, large, extra-large
                        primary_action_label: 'Submit',
                        primary_action(data) {
                            dialog2.hide();
                        }
                    });
                    dialog1.hide();
                }
            });
        }
    });

    dialog1.show();
}
