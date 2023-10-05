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

/**
 * Create a dialog where entity can be recovered by Sirene API
 */
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
                    if (response.message.error) {
                        return
                    }

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

/**
 * Display a Dialog where entity can be selected
 */
function selectEntity(etablissements) {
    let options = [];
    let entities = [];
    for (let entity of etablissements) {
        entityInfo = findInfoEntity(entity)
        options.push(entityInfo.title);
        entities.push(entityInfo);
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

            new_doc = createNewDocWithSireneInfo(doctype, entity_chosen)

            frappe.ui.form.make_quick_entry(doctype, null, null, new_doc);
            dialog2.hide();
        }
    });
    dialog2.show();
}

/**
 * Look into Sirene API object returned and get needed entity info
 */
function findInfoEntity(entity) {
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

    if (entity.uniteLegale.denominationUniteLegale && !entity.uniteLegale.nomUsageUniteLegale) {
        let company_name = '';
        entity_type = 'Company';
        // Morale
        company_name = entity.uniteLegale.denominationUniteLegale;
        if (entity.uniteLegale.denominationUsuelle1UniteLegale) {
            company_name_alias = entity.uniteLegale.denominationUsuelle1UniteLegale;
        } else if(entity.uniteLegale.denominationUsuelle2UniteLegale) {
            company_name_alias = entity.uniteLegale.denominationUsuelle2UniteLegale;
        } else if (entity.uniteLegale.denominationUsuelle2UniteLegale) {
            company_name_alias = entity.uniteLegale.denominationUsuelle2UniteLegale;
        } else if(entity.periodesEtablissement[0]) {
            let entityinfo = entity.periodesEtablissement[0];
            company_name_alias = entityinfo.denominationUsuelleEtablissement;

            if (!company_name_alias){
                if (entityinfo.enseigne1Etablissement) {
                    company_name_alias = entityinfo.enseigne1Etablissement;
                } else if (entityinfo.enseigne2Etablissement) {
                    company_name_alias = entityinfo.enseigne2Etablissement;
                } else if (entityinfo.enseigne3Etablissement) {
                    company_name_alias = entityinfo.enseigne3Etablissement;
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
        let company_name = entity.uniteLegale.nomUsageUniteLegale;
        let firstname = entity.uniteLegale.prenomUsuelUniteLegale;

        if (!firstname){
            if (entity.uniteLegale.prenom1UniteLegale) {
                firstname = entity.uniteLegale.prenom1UniteLegale;
            } else if (entity.uniteLegale.prenom2UniteLegale) {
                firstname = entity.uniteLegale.prenom2UniteLegale;
            } else if (entity.uniteLegale.prenom3UniteLegale) {
                firstname = entity.uniteLegale.prenom3UniteLegale;
            } else if (entity.uniteLegale.prenom4UniteLegale) {
                firstname = entity.uniteLegale.prenom4UniteLegale;
            }
        } else {
            if (entity.uniteLegale.prenom1UniteLegale) {
                company_name_alias = entity.uniteLegale.prenom1UniteLegale;
            } else if (entity.uniteLegale.prenom2UniteLegale) {
                company_name_alias = entity.uniteLegale.prenom2UniteLegale;
            } else if (entity.uniteLegale.prenom3UniteLegale) {
                company_name_alias = entity.uniteLegale.prenom3UniteLegale;
            } else if (entity.uniteLegale.prenom4UniteLegale) {
                company_name_alias = entity.uniteLegale.prenom4UniteLegale;
            }
        }

        company_name_all = firstname + ' ' + company_name;
    }

    if (company_name_alias) {
        company_name_all += ' (' + company_name_alias + ')';
    }

    if (entity.dateCreationEtablissement) {
        date_creation = entity.dateCreationEtablissement;
    }

    if (entity.adresseEtablissement.numeroVoieEtablissement) {
        address_1 = entity.adresseEtablissement.numeroVoieEtablissement;
    }

    if (entity.adresseEtablissement.typeVoieEtablissement) {
        address_1 = entity.adresseEtablissement.typeVoieEtablissement;
    }

    if (entity.adresseEtablissement.libelleVoieEtablissement) {
        address_1 += ' ' + entity.adresseEtablissement.libelleVoieEtablissement;
    }

    if (entity.adresseEtablissement.libelleCommuneEtablissement) {
        town = entity.adresseEtablissement.libelleCommuneEtablissement;
    }

    if (entity.adresseEtablissement.codePostalEtablissement) {
        zipcode = entity.adresseEtablissement.codePostalEtablissement;
    }

    if (entity.adresseEtablissement.libellePaysEtrangerEtablissement) {
        country = entity.adresseEtablissement.libellePaysEtrangerEtablissement;
    }

    if (entity.siren) {
        siren = entity.siren;
    }

    if (entity.siret) {
        siret = entity.siret;
    }

    if (entity.uniteLegale.activitePrincipaleUniteLegale) {
        code_naf = entity.uniteLegale.activitePrincipaleUniteLegale;
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

    entityInfo = {
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
    }

    return entityInfo;
}

/**
 * Init Doctype with Sirene Info
 */
function createNewDocWithSireneInfo(doctype, entity_chosen) {
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

    return new_doc
}
