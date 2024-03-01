// Copyright (c) 2023, scopen.fr and contributors
// For license information, please see license.txt


frappe.listview_settings["Customer"] = {
	onload(listview) {
		if (listview.can_create) {
			listview.page.add_inner_button(__('Import customer from SIRENE'), import_thirdparty_from_sirene, '', 'primary')
		}
	},
};

frappe.listview_settings["Supplier"] = {
	onload(listview) {
		if (listview.can_create) {
			listview.page.add_inner_button(__('Import supplier from SIRENE'), import_thirdparty_from_sirene, '', 'primary')
		}
	},
};

/**
 * Create a dialog where entity can be recovered by Sirene API
 */
function import_thirdparty_from_sirene() {
	let dialog1 = new frappe.ui.Dialog({
		title: __('Enter entity details'),
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
				fieldtype: 'Data',
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
		primary_action_label: __('Search'),
		primary_action(data) {
			frappe.call({
				method: "erpnext_france.controllers.fetch_company_from_sirene.fetch_company_from_sirene",
				args: {data},
				callback: function (response) {
					if (!response || !response.message) {
						frappe.throw(__('No Response From Server'));
						return
					}

					dialog1.hide();
					if (response.message.error) {
						return
					}

					if (!response.message.message.etablissements) {
						frappe.throw(__('No Entity Found With Those Info'));
						return
					}

					selectEntity(response.message.message.etablissements);

				}
			});
		}
	});

	frappe.db.get_doc('ERPNext France Settings', null)
		.then(doc => {
			if (!doc.api_token || !doc.api_url) {
				frappe.throw(__('You have to specify Erpnext France Parameters'))
			} else {
				dialog1.show();
			}
		})
}

/**
 * Display a Dialog where entity can be selected
 */
function selectEntity(etablissements) {
	let options = [];
	let entities = [];
	let i = 0;
	for (let entity of etablissements) {
		entityInfo = findInfoEntity(entity, i)
		options.push(entityInfo.title);
		entities.push(entityInfo);
		i++;
	}

	var route_attributes = frappe.get_route();
	doctype = route_attributes[1];

	let dialog2 = new frappe.ui.Dialog({
		title: __('Select Entity'),
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "table_area",
			},
		],
		size: 'extra-large', // small, large, extra-large
		primary_action_label: __('Submit'),
		async primary_action() {
			selected = $(this.$wrapper[0]).find('input[name="entity-select"]:checked');
			if (selected.length > 0) {
				let entity_chosen;
				for (let entity of entities) {
					if (entity.id === parseInt(selected.val())) {
						entity_chosen = entity;
						break;
					}
				}

				new_doc = await createNewDocWithSireneInfo(doctype, entity_chosen);
				frappe.ui.form.make_quick_entry(doctype, null, null, new_doc);
				dialog2.hide();
			}
		}
	});

	let $wrapper = dialog2.fields_dict.table_area.$wrapper.append(
		`<div class="results my-3" style="border: 1px solid #d1d8dd; border-radius: 3px; height: 300px; overflow: auto;"></div>`
	);

	let $results = $wrapper.find(".results");
	$results.append(make_table(entities, doctype));
	dialog2.show();
}

/**
 * Look into Sirene API object returned and get needed entity info
 */
function findInfoEntity(entity, i) {
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
	let legal_form = '';

	if (entity.uniteLegale.denominationUniteLegale && !entity.uniteLegale.nomUsageUniteLegale) {
		let company_name = '';
		entity_type = 'Company';
		// Morale
		company_name = entity.uniteLegale.denominationUniteLegale;
		if (entity.uniteLegale.denominationUsuelle1UniteLegale) {
			company_name_alias = entity.uniteLegale.denominationUsuelle1UniteLegale;
		} else if (entity.uniteLegale.denominationUsuelle2UniteLegale) {
			company_name_alias = entity.uniteLegale.denominationUsuelle2UniteLegale;
		} else if (entity.uniteLegale.denominationUsuelle2UniteLegale) {
			company_name_alias = entity.uniteLegale.denominationUsuelle2UniteLegale;
		} else if (entity.periodesEtablissement[0]) {
			let entityinfo = entity.periodesEtablissement[0];
			company_name_alias = entityinfo.denominationUsuelleEtablissement;

			if (!company_name_alias) {
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

		if (!firstname) {
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

		company_name_all = firstname + ' ' + (company_name ? company_name : '');
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
		address_1 += ' ' + entity.adresseEtablissement.typeVoieEtablissement;
	}

	if (entity.adresseEtablissement.libelleVoieEtablissement) {
		address_1 += ' ' + entity.adresseEtablissement.libelleVoieEtablissement;
	}

	if (entity.adresseEtablissement.complementAdresseEtablissement) {
		address_1 += ' ' + entity.adresseEtablissement.complementAdresseEtablissement;
	}

	if (entity.adresseEtablissement.libelleCommuneEtablissement) {
		town = entity.adresseEtablissement.libelleCommuneEtablissement;
	} else if (entity.adresseEtablissement.libelleCommuneEtrangerEtablissement) {
		town = entity.adresseEtablissement.libelleCommuneEtrangerEtablissement;
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
		code_naf = code_naf.replace('.', '');
	}

	if (entity.uniteLegale.categorieJuridiqueUniteLegale) {
		legal_form = entity.uniteLegale.categorieJuridiqueUniteLegale;
		legal_form = legal_form.substr(0, 2);
	}

	// intra-community vat number calculation
	let coef = 97;
	let vatintracalc = parseInt(siren) % coef
	let vatintracalc2 = leftFillNum((12 + 3 * vatintracalc) % coef, 2);
	let tva_intra = 'FR' + vatintracalc2 + siren

	entityInfo = {
		company_name: company_name_all,
		entity_type: entity_type,
		address_1: address_1,
		zipcode: zipcode,
		town: town,
		country: country,
		date_creation: date_creation,
		siren: siren,
		siret: siret,
		code_naf: code_naf,
		legal_form: legal_form,
		tax_id: tva_intra,
		id: i
	}

	return entityInfo;
}

/**
 * Init Doctype with Sirene Info
 */
async function createNewDocWithSireneInfo(doctype, entity_chosen) {
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
	new_doc.code_naf = await getCodeNaf(entity_chosen.code_naf);
	new_doc.legal_form = await getLegalForm(entity_chosen.legal_form);
	new_doc.tax_id = entity_chosen.tax_id;


	return new_doc
}

function make_table(entities, doctype) {
	let contents = ``;
	columns = ['radio', 'company_name', 'address1', 'creation_date', 'code_naf', 'siren', 'siret']

	table =
		'<div class="form-grid-container">'
		+ '    <div class="form-grid">'
		+ '        <div class="grid-heading-row">'
		+ '            <div class="grid-row">'
		+ '               <div class="data-row row">'
		+ '                   <div class="col grid-static-col col-xs-3 ">'
		+ '                       <span class="static-area ellipsis bold">' + __('Company Name') + '</span>'
		+ '                   </div>'
		+ '                   <div class="col grid-static-col col-xs-3">'
		+ '                       <span class="static-area ellipsis bold">' + __('Address') + '</span>'
		+ '                   </div>'
		+ '                   <div class="col grid-static-col col-xs-2">'
		+ '                       <span class="static-area ellipsis bold">' + __('Creation Date') + '</span>'
		+ '                   </div>'
		+ '                   <div class="col grid-static-col col-xs-1">'
		+ '                       <span class="static-area ellipsis bold">' + __('NAF') + '</span>'
		+ '                   </div>'
		+ '                   <div class="col grid-static-col col-xs-1">'
		+ '                       <span class="static-area ellipsis bold">' + __('SIREN') + '</span>'
		+ '                   </div>'
		+ '                   <div class="col grid-static-col col-xs-1">'
		+ '                       <span class="static-area ellipsis bold">' + __('SIRET') + '</span>'
		+ '                   </div>'
		+ '               </div>'
		+ '            </div>'
		+ '        </div>';
	+'        <div class="grid-body">'
	+ '            <div class="rows">'
	for (entity of entities) {
		table +=
			'            <div class="grid-row">'
			+ '               <div class="data-row row">'
			+ '                   <div class="col grid-static-col col-xs-3 bold" style="height: auto !important;">'
			+ '                       <input name="entity-select" class="grid-row-check" type="radio" value="' + entity.id + '">'
			+ '                       <span class="static-area ellipsis" style="white-space: normal !important;">' + entity.company_name + '</span>'
			+ '                   </div>'
			+ '                   <div class="col grid-static-col col-xs-3" style="height: auto !important;">'
			+ '                       <span class="static-area ellipsis" style="white-space: normal !important;">'
			+ entity.address_1 + ' ' + entity.zipcode + ' ' + entity.town
			+ '                        </span>'
			+ '                   </div>'
			+ '                   <div class="col grid-static-col col-xs-2">'
			+ '                       <span class="static-area ellipsis">' + entity.date_creation + '</span>'
			+ '                   </div>'
			+ '                   <div class="col grid-static-col col-xs-1">'
			+ '                       <span class="col grid-static-col col-xs-2">' + entity.code_naf + '</span>'
			+ '                   </div>'
			+ '                   <div class="col grid-static-col col-xs-1">'
			+ '                       <span class="static-area ellipsis">' + entity.siren + '</span>'
			+ '                   </div>'
			+ '                   <div class="col grid-static-col col-xs-1">'
			+ '                       <span class="static-area ellipsis">' + entity.siret + '</span>'
			+ '                   </div>'
			+ '               </div>'
			+ '           </div>';

	}

	table +=
		'           </div>'
		+ '     </div>';
	+' </div>';


	return table;
}

function leftFillNum(num, targetLength) {
	return num.toString().padStart(targetLength, "0");
}

async function getCodeNaf(code_naf) {
	let naf = await frappe.db.get_doc('Code Naf', null, {code: code_naf});
	return naf.name
}

async function getLegalForm(legal_form) {
	let form = await frappe.db.get_doc('Legal Form', null, {code: legal_form});
	return form.name
}
