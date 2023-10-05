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
                    dialog1.hide();
                    if (! response.message.message.etablissements) {
                        frappe.throw(__('No Entity Found With Those Info'));
                        return
                    }

                    selectEntity(response.message.message.etablissements);

                }
            });
        }
    });

    dialog1.show();
}

function selectEntity(etablissements) {
    let options = [];
    let entities = [];
    for (let etablissement of etablissements) {
        let stringToShow = '';
        let company_name_alias = '';
        let company_name_all = '';
        let date_creation = '';
        let address_1 = '';
        let town = '';
        let zipcode = '';
        let country = 'France';
        let siren = '';
        let siret = '';
        let naf = '';
        let entity_type = '';

        if (etablissement.uniteLegale.denominationUniteLegale && !etablissement.uniteLegale.nomUsageUniteLegale) {
            let company_name = '';
            entity_type = 'Company';
            // Morale
            company_name = etablissement.uniteLegale.denominationUniteLegale;
            if (etablissement.uniteLegale.denominationUsuelle1UniteLegale) {
                company_name_alias = etablissement.uniteLegale.denominationUsuelle1UniteLegale;
            } else if(etablissement.uniteLegale.denominationUsuelle2UniteLegale) {
                company_name_alias = etablissement.uniteLegale.denominationUsuelle2UniteLegale;
            } else if (etablissement.uniteLegale.denominationUsuelle2UniteLegale) {
                company_name_alias = etablissement.uniteLegale.denominationUsuelle2UniteLegale;
            } else if(etablissement.periodesEtablissement[0]) {
                let etablissementinfo = etablissement.periodesEtablissement[0];
                company_name_alias = etablissementinfo.denominationUsuelleEtablissement;

                if (!company_name_alias){
                    if (etablissementinfo.enseigne1Etablissement) {
                        company_name_alias = etablissementinfo.enseigne1Etablissement;
                    } else if (etablissementinfo.enseigne2Etablissement) {
                        company_name_alias = etablissementinfo.enseigne2Etablissement;
                    } else if (etablissementinfo.enseigne3Etablissement) {
                        company_name_alias = etablissementinfo.enseigne3Etablissement;
                    }
                }
            }

            if (company_name === company_name_alias) {
                company_name_alias = '';
            }

            company_name_all = company_name;
        } else {
            // Physique
            entity_type = 'Individual';
            let company_name = etablissement.uniteLegale.nomUsageUniteLegale;
            let firstname = etablissement.uniteLegale.prenomUsuelUniteLegale;

            if (!firstname){
                if (etablissement.uniteLegale.prenom1UniteLegale) {
                    firstname = etablissement.uniteLegale.prenom1UniteLegale;
                } else if (etablissement.uniteLegale.prenom2UniteLegale) {
                    firstname = etablissement.uniteLegale.prenom2UniteLegale;
                } else if (etablissement.uniteLegale.prenom3UniteLegale) {
                    firstname = etablissement.uniteLegale.prenom3UniteLegale;
                } else if (etablissement.uniteLegale.prenom4UniteLegale) {
                    firstname = etablissement.uniteLegale.prenom4UniteLegale;
                }
            } else {
                if (etablissement.uniteLegale.prenom1UniteLegale) {
                    company_name_alias = etablissement.uniteLegale.prenom1UniteLegale;
                } else if (etablissement.uniteLegale.prenom2UniteLegale) {
                    company_name_alias = etablissement.uniteLegale.prenom2UniteLegale;
                } else if (etablissement.uniteLegale.prenom3UniteLegale) {
                    company_name_alias = etablissement.uniteLegale.prenom3UniteLegale;
                } else if (etablissement.uniteLegale.prenom4UniteLegale) {
                    company_name_alias = etablissement.uniteLegale.prenom4UniteLegale;
                }
            }

            company_name_all = firstname + ' ' + company_name;
        }

        if (company_name_alias) {
            company_name_all += ' (' + company_name_alias + ')';
        }

        if (etablissement.dateCreationEtablissement) {
            date_creation = etablissement.dateCreationEtablissement;
        }

        if (etablissement.adresseEtablissement.numeroVoieEtablissement) {
            address_1 = etablissement.adresseEtablissement.numeroVoieEtablissement;
        }

        if (etablissement.adresseEtablissement.typeVoieEtablissement) {
            address_1 = etablissement.adresseEtablissement.typeVoieEtablissement;
        }

        if (etablissement.adresseEtablissement.libelleVoieEtablissement) {
            address_1 += ' ' + etablissement.adresseEtablissement.libelleVoieEtablissement;
        }

        if (etablissement.adresseEtablissement.libelleCommuneEtablissement) {
            town = etablissement.adresseEtablissement.libelleCommuneEtablissement;
        }

        if (etablissement.adresseEtablissement.codePostalEtablissement) {
            zipcode = etablissement.adresseEtablissement.codePostalEtablissement;
        }

        if (etablissement.adresseEtablissement.libellePaysEtrangerEtablissement) {
            country = etablissement.adresseEtablissement.libellePaysEtrangerEtablissement;
        }

        if (etablissement.siren) {
            siren = etablissement.siren;
        }

        if (etablissement.siret) {
            siret = etablissement.siret;
        }

        if (etablissement.uniteLegale.activitePrincipaleUniteLegale) {
            code_naf = etablissement.uniteLegale.activitePrincipaleUniteLegale;
        }

        title = company_name_all
            + ':  ' + address_1
            + ' ' + town
            + ' ' + zipcode
            + ' ' + country
            + ' ' + date_creation
            + ' Siren: ' + siren
            + ' Siret: ' + siret
            + ' Code Naf: ' + code_naf;

        options.push(title);

        entities.push({
          company_name: company_name_all,
          entity_type: entity_type,
          address_1: address_1,
          town : town,
          zipcode: zipcode,
          country: country,
          date_creation: date_creation,
          siren: siren,
          siret: siret,
          code_naf: code_naf,
          title: title
        });
    }
    let dialog2 = new frappe.ui.Dialog({
        title: __('Select Entity'),
        fields: [
            {
                label: 'Entity',
                fieldname: 'entity',
                fieldtype: 'Select',
                options: options,
            },
        ],
        size: 'large', // small, large, extra-large
        primary_action_label: 'Submit',
        primary_action(selected) {
            let entity_chosen;
            for (let entity of entities) {
                if (entity.title === selected.entity) {
                    entity_chosen = entity;
                    break;
                }
            }

            var route_attributes = frappe.get_route();
            doctype = route_attributes[1];
            var new_doc = frappe.model.get_new_doc(doctype);

            if (doctype == 'Customer') {
                new_doc.customer_name = entity_chosen.company_name;
                new_doc.customer_type = entity_chosen.entity_type;
            } else {
                new_doc.supplier_name = entity_chosen.company_name;
                new_doc.supplier_type = entity_chosen.entity_type;
            }

            new_doc.address_line1 = entity_chosen.address_1;
            new_doc.city = entity_chosen.town;
            new_doc.pincode = entity_chosen.zipcode;
            new_doc.country = entity_chosen.country;
            new_doc.siret = entity_chosen.siret;
            new_doc.siren = entity_chosen.siren;
            new_doc.naf = entity_chosen.code_naf;

            frappe.ui.form.make_quick_entry(doctype, null, null, new_doc);
            dialog2.hide();
        }
    });
    dialog2.show();
}
