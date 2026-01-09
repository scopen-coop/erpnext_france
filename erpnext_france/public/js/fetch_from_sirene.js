// Copyright (c) 2023, scopen.fr and contributors
// For license information, please see license.txt

frappe.listview_settings["Customer"] = {
  onload(listview) {
    if (listview.can_create) {
      listview.page.add_inner_button(
        __("Import customer from SIRENE"),
        import_thirdparty_from_sirene,
        "",
        "primary"
      );
    }
  },
};

frappe.ui.form.on("Customer", {
  refresh(frm) {
    frm.page.add_inner_button(
      __('Update customer from SIRENE'),
      function () {
        update_thirdparty_from_sirene(frm);
      },
      "",
      "primary");
  }
})

frappe.ui.form.on("Supplier", {
  refresh(frm) {
    frm.page.add_inner_button(
      __("Update supplier from SIRENE"),
      function () {
        update_thirdparty_from_sirene(frm);
      },
      "",
      "primary");
  }
})


frappe.listview_settings["Supplier"] = {
  onload(listview) {
    if (listview.can_create) {
      listview.page.add_inner_button(
        __("Import supplier from SIRENE"),
        import_thirdparty_from_sirene,
        "",
        "primary"
      );
    }
  },
};

/**
 * Create a dialog where entity can be recovered by Sirene API
 */
function import_thirdparty_from_sirene() {
  let dialog1 = new frappe.ui.Dialog({
    title: __("Enter entity details"),
    fields: [
      {
        label: "Company Name",
        fieldname: "company_name",
        fieldtype: "Data",
      },
      {
        label: "SIREN",
        fieldname: "siren",
        fieldtype: "Data",
      },
      {
        label: "SIRET",
        fieldname: "siret",
        fieldtype: "Data",
      },
      {
        label: "NAF",
        fieldname: "naf",
        fieldtype: "Data",
      },
      {
        label: "Zipcode",
        fieldname: "zipcode",
        fieldtype: "Data",
      },
      {
        label: "Nb of displayed results",
        fieldname: "nb_results",
        fieldtype: "Int",
        default: 20,
      },
    ],
    size: "large", // small, large, extra-large
    primary_action_label: __("Search"),
    primary_action(data) {
      frappe.call({
        method:
          "erpnext_france.controllers.fetch_company_from_sirene.fetch_company_from_sirene",
        args: {data},
        callback: function (response) {
          if (!response || !response.message) {
            frappe.throw(__("No Response From Server"));
            return;
          }

          dialog1.hide();
          if (response.message.error) {
            return;
          }

          if (!response.message.message.etablissements) {
            frappe.throw(__("No Entity Found With Those Info"));
            return;
          }

          selectEntity(response.message.message.etablissements);
        },
      });
    },
  });

  frappe.db.get_doc("ERPNext France Settings", null).then((doc) => {
    if (!doc.api_token || !doc.api_url) {
      frappe.throw(__("You have to specify Erpnext France Parameters"));
    } else {
      dialog1.show();
    }
  });
}

/**
 * Display a Dialog where entity can be selected
 */
function selectEntity(etablissements) {
  let options = [];
  let entities = [];
  let i = 0;
  for (let entity of etablissements) {
    entityInfo = findInfoEntity(entity, i);
    options.push(entityInfo.title);
    entities.push(entityInfo);
    i++;
  }

  var route_attributes = frappe.get_route();
  doctype = route_attributes[1];

  let dialog2 = new frappe.ui.Dialog({
    title: __("Select Entity"),
    fields: [
      {
        fieldtype: "HTML",
        fieldname: "table_area",
      },
    ],
    size: "extra-large", // small, large, extra-large
    primary_action_label: __("Submit"),
    async primary_action() {
      selected = $(this.$wrapper[0]).find(
        'input[name="entity-select"]:checked'
      );
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
    },
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
  let company_name_alias = "";
  let company_name_all = "";
  let date_creation = "";
  let address_1 = "";
  let town = "";
  let zipcode = "";
  let country = "France";
  let siren = "";
  let siret = "";
  let naf = "";
  let entity_type = "";
  let legal_form = "";

  if (
    entity.uniteLegale.denominationUniteLegale &&
    !entity.uniteLegale.nomUsageUniteLegale
  ) {
    let company_name = "";
    entity_type = "Company";
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
      company_name_alias = "";
    }

    company_name_all = company_name;
  } else {
    // Physique
    entity_type = "Individual";
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

    company_name_all = firstname + " " + (company_name ? company_name : "");
  }

  if (company_name_alias) {
    company_name_all += " (" + company_name_alias + ")";
  }

  if (entity.dateCreationEtablissement) {
    date_creation = entity.dateCreationEtablissement;
  }

  if (entity.adresseEtablissement.numeroVoieEtablissement) {
    address_1 = entity.adresseEtablissement.numeroVoieEtablissement;
  }

  if (entity.adresseEtablissement.typeVoieEtablissement) {
    address_1 += " " + entity.adresseEtablissement.typeVoieEtablissement;
  }

  if (entity.adresseEtablissement.libelleVoieEtablissement) {
    address_1 += " " + entity.adresseEtablissement.libelleVoieEtablissement;
  }

  if (entity.adresseEtablissement.complementAdresseEtablissement) {
    address_1 +=
      " " + entity.adresseEtablissement.complementAdresseEtablissement;
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
    code_naf = code_naf.replace(".", "");
  }

  if (entity.uniteLegale.categorieJuridiqueUniteLegale) {
    legal_form = entity.uniteLegale.categorieJuridiqueUniteLegale;
  }

  // intra-community vat number calculation
  let coef = 97;
  let vatintracalc = parseInt(siren) % coef;
  let vatintracalc2 = leftFillNum((12 + 3 * vatintracalc) % coef, 2);
  let tva_intra = "FR" + vatintracalc2 + siren;

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
    id: i,
  };

  return entityInfo;
}

/**
 * Init Doctype with Sirene Info
 */
async function createNewDocWithSireneInfo(doctype, entity_chosen) {
  var new_doc = frappe.model.get_new_doc(doctype);

  if (doctype == "Customer") {
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

  return new_doc;
}

function make_table(entities, doctype) {
  let contents = ``;
  columns = [
    "radio",
    "company_name",
    "address1",
    "creation_date",
    "code_naf",
    "siren",
    "siret",
  ];

  table =
    '<div class="form-grid-container">' +
    '    <div class="form-grid">' +
    '        <div class="grid-heading-row">' +
    '            <div class="grid-row">' +
    '               <div class="data-row row">' +
    '                   <div class="col grid-static-col col-xs-3 ">' +
    '                       <span class="static-area ellipsis bold">' +
    __("Company Name") +
    "</span>" +
    "                   </div>" +
    '                   <div class="col grid-static-col col-xs-3">' +
    '                       <span class="static-area ellipsis bold">' +
    __("Address") +
    "</span>" +
    "                   </div>" +
    '                   <div class="col grid-static-col col-xs-2">' +
    '                       <span class="static-area ellipsis bold">' +
    __("Creation Date") +
    "</span>" +
    "                   </div>" +
    '                   <div class="col grid-static-col col-xs-1">' +
    '                       <span class="static-area ellipsis bold">' +
    __("NAF") +
    "</span>" +
    "                   </div>" +
    '                   <div class="col grid-static-col col-xs-1">' +
    '                       <span class="static-area ellipsis bold">' +
    __("SIREN") +
    "</span>" +
    "                   </div>" +
    '                   <div class="col grid-static-col col-xs-1">' +
    '                       <span class="static-area ellipsis bold">' +
    __("SIRET") +
    "</span>" +
    "                   </div>" +
    "               </div>" +
    "            </div>" +
    "        </div>";
  +'        <div class="grid-body">' + '            <div class="rows">';
  for (entity of entities) {
    table +=
      '            <div class="grid-row">' +
      '               <div class="data-row row">' +
      '                   <div class="col grid-static-col col-xs-3 bold" style="height: auto !important;">' +
      '                       <input name="entity-select" class="grid-row-check" type="radio" value="' +
      entity.id +
      '">' +
      '                       <span class="static-area ellipsis" style="white-space: normal !important;">' +
      entity.company_name +
      "</span>" +
      "                   </div>" +
      '                   <div class="col grid-static-col col-xs-3" style="height: auto !important;">' +
      '                       <span class="static-area ellipsis" style="white-space: normal !important;">' +
      entity.address_1 +
      " " +
      entity.zipcode +
      " " +
      entity.town +
      "                        </span>" +
      "                   </div>" +
      '                   <div class="col grid-static-col col-xs-2">' +
      '                       <span class="static-area ellipsis">' +
      entity.date_creation +
      "</span>" +
      "                   </div>" +
      '                   <div class="col grid-static-col col-xs-1">' +
      '                       <span class="col grid-static-col col-xs-2">' +
      entity.code_naf +
      "</span>" +
      "                   </div>" +
      '                   <div class="col grid-static-col col-xs-1">' +
      '                       <span class="static-area ellipsis">' +
      entity.siren +
      "</span>" +
      "                   </div>" +
      '                   <div class="col grid-static-col col-xs-1">' +
      '                       <span class="static-area ellipsis">' +
      entity.siret +
      "</span>" +
      "                   </div>" +
      "               </div>" +
      "           </div>";
  }

  table += "           </div>" + "     </div>";
  +" </div>";

  return table;
}

/**
 * Create a dialog where entity fields can be recovered by Sirene API
 */
function update_thirdparty_from_sirene(frm) {
  let currentDoc = frm.doc
  $(document).on('click', '.addRemoveArrow', function () {
    const $btn = $(this);
    const $use = $btn.find('use');
    const currentDirection = $btn.data('direction');
    const currentField = $btn.data('field');

    if (currentDirection === 'left') {
      $use.attr('href', '#icon-close');
      $btn.data('direction', 'right');

      const previousValue = $btn.closest("tr").find(".currentValue").val()
      const newValue = $btn.closest("tr").find(".retrievedValue").val()
      $btn.closest("tr").find(".currentValue").val(newValue)
      $btn.closest("tr").find(".currentValue").data('previousValue', previousValue);
      $btn.closest("tr").find(".currentValue").data('updated', true);
    } else {
      $use.attr('href', '#es-line-left-chevron');
      $btn.data('direction', 'left');

      const previousValue = $btn.closest("tr").find(".currentValue").data('previousValue')

      $btn.closest("tr").find(".currentValue").val(previousValue)
      $btn.closest("tr").find(".currentValue").data('previousValue', '');
      $btn.closest("tr").find(".currentValue").data('updated', false);
    }

    $("#sirene_mismatch_" + currentField).hide()
    $("#sirene_match_" + currentField).show()


  });


  let data = null
  const {sirene, siret} = frm.doc;
  if (siret !== null) {
    data = {siret}
  } else if (sirene !== null) {
    data = {sirene}
  } else {
    frappe.throw(__("SIRET or SIRENE must be specified to retrieve a third party"));
  }

  frappe.db.get_doc("ERPNext France Settings", null).then((doc) => {
    if (!doc.api_token || !doc.api_url) {
      frappe.throw(__("You have to specify Erpnext France Parameters"));
    } else {
      frappe.call({
        freeze: true,
        freeze_message: __("Retrieving data..."),
        method:
          "erpnext_france.controllers.fetch_company_from_sirene.fetch_company_from_siret_or_siren",
        args: {data},
        callback: function (response) {
          if (!response || !response.message) {
            frappe.throw(__("No Response From Server"));
            return;
          }

          if (response.message.error) {
            return;
          }

          if (!response.message.message.etablissements) {
            frappe.throw(__("No Entity Found With Those Info"));
            return;
          }
          selectFields(frm, currentDoc, response.message.message.etablissements[0]);
        },
      });
    }
  });
}

/**
 * Display a Dialog where entity can be selected
 */
async function selectFields(frm, currentDoc, etablissement) {
  let response = await frappe.call({
    method: 'erpnext_france.controllers.fetch_company_from_sirene.get_entity_info',
    args: {
      entity: etablissement,
      i: 0,
    },
    callback: function (response) {
      if (!response || !response.hasOwnProperty('message')) {
        frappe.throw(__("No Response From Server"));
      }
    }
  })
  let entity = response.message

  let AddressDoc = await getAddressDoctype(currentDoc)

  let doctype

  switch (currentDoc.doctype) {
    case "Customer":
      doctype =
        {
          'type': 'Customer',
          'field_name': 'customer_name',
          'field_type': 'customer_type',
          'field_address': 'customer_primary_address',
        }
      break;
    case "Supplier":
      doctype =
        {
          'type': 'Supplier',
          'field_name': 'supplier_name',
          'field_type': 'supplier_type',
          'field_address': 'supplier_primary_address',
        }
      break;
  }

  frappe.call({
    method: 'erpnext_france.controllers.fetch_company_from_sirene.compare_values',
    args: {
      doctype: doctype,
      element: currentDoc,
      address: AddressDoc,
      entity_info: entity,
    },
    callback: function (response) {
      if (!response || !response.hasOwnProperty('message')) {
        frappe.throw(__("No Response From Server"));
        return
      }
      const match = response.message

      if (match) {
        frappe.msgprint({
          title: __('Perfect Match'),
          indicator: 'green',
          message: __('Document is up-to-date')
        });
        return
      }


      let dialog3 = new frappe.ui.Dialog({
        title: currentDoc.doctype === "Customer" ? __("Update customer") : __("Update supplier"),
        fields: [
          {
            fieldtype: "HTML",
            fieldname: "table_area",
          },
        ],
        size: "extra-large", // small, large, extra-large
        primary_action_label: __("Update"),
        secondary_action_label: __("Update all"),
        onhide: function () {
          this.$wrapper.remove();
          dialog3 = null;
        },
        async primary_action() {
          frappe.dom.freeze(__("Updating data..."));
          await updateFieldsWithSireneInfo(frm, doctype.type, AddressDoc)
          frappe.dom.unfreeze()
          dialog3.hide();
        },
        async secondary_action() {
          frappe.dom.freeze(__("Updating data..."));

          try {
            await update_doc_with_sirene_info(frm.doc, entity, doctype.type, AddressDoc)

            await frm.reload_doc();

            frappe.show_alert({
              message: doctype === "Customer"
                ? __('Customer successfully updated')
                : __('Supplier successfully updated'),
              indicator: 'green'
            });
          } catch (error) {
            console.error('Error:', error);
            frappe.msgprint({
              title: __('Error'),
              indicator: 'red',
              message: __('Error while updating')
            });
          } finally {
            frappe.dom.unfreeze();
          }


          frappe.dom.unfreeze()
          dialog3.hide();
        },
      });

      dialog3.fields_dict.table_area.$wrapper.append(
        make_table_update(currentDoc, entity, AddressDoc)
      );

      dialog3.$wrapper.find('.btn-secondary')
        .removeClass('btn-secondary')
        .addClass('btn-warning');
      dialog3.$wrapper.find('.modal-footer').prepend(
        `<button class="btn btn-default btn-sm" data-action="third-action"> ${__("Cancel")}</button>`
      );

      dialog3.$wrapper.find('[data-action="third-action"]').on('click', function () {
        dialog3.hide();
      });

      dialog3.show()

    },
  });
}

function make_table_update(currentDoc, entity, AddressDoc) {

  return `
  <div class="updateFields my-3" style="border-radius: 3px; overflow: auto;">
    <table style="width: 100%; border-collapse: collapse;padding: 2px;">
        <tbody>
            <tr>
                <td>
                    <label style="display: block;">${__("Company Name")}</label>
                </td>
                <td>
                    <input class="input-with-feedback form-control currentValue" value="${currentDoc.doctype === 'Customer' ? currentDoc.customer_name : currentDoc.supplier_name}"/>
                </td>
                <td style="width:100px" class="center">` +
    sirenePrintCheckbox(currentDoc.doctype === 'Customer' ? 'customer_name' : 'supplier_name', checkValue([
      {fname: 'company_name', dval: currentDoc.doctype === 'Customer' ? currentDoc.customer_name : currentDoc.supplier_name, sval: entity.company_name}
    ])) + `</td>
                <td>
                    <input id="sirene_company_name" class="input-with-feedback form-control retrievedValue" value="` + entity.company_name + `" />
                </td>
            </tr>
            <tr>
                <td>
                    <label style="display: block;">${__("Address")}</label>
                </td>
                <td>
                    <input class="input-with-feedback form-control currentValue" value="` + AddressDoc.address_line1 + `"/>
                </td>
                <td class="center">` + sirenePrintCheckbox('company_address', checkValue([
      {fname: 'company_address', dval: AddressDoc.address_line1, sval: entity.address_1}
    ])) + `</td>
                <td>
                    <input id="sirene_company_address" class="input-with-feedback form-control retrievedValue" value="` + entity.address_1 + `" />
                </td>
            </tr>
            <tr>
                <td>
                    <label style="display: block;">${__("Zipcode")}</label>
                </td>
                <td>
                    <input class="input-with-feedback form-control currentValue" value="` + AddressDoc.pincode + `"/>
                </td>
                <td class="center">` + sirenePrintCheckbox('company_pincode', checkValue([
      {fname: 'company_pincode', dval: AddressDoc.pincode, sval: entity.zipcode}
    ])) + `</td>
                <td>
                    <input id="sirene_company_pincode" class="input-with-feedback form-control retrievedValue" value="` + entity.zipcode + `" />
                </td>
            </tr>
            <tr>
                <td>
                    <label style="display: block;">${__("City")}</label>
                </td>
                <td>
                    <input class="input-with-feedback form-control currentValue" value="` + AddressDoc.city + `"/>
                </td>
                <td class="center">` + sirenePrintCheckbox('company_city', checkValue([
      {fname: 'company_city', dval: AddressDoc.city, sval: entity.town}
    ])) + `</td>
                <td>
                    <input id="sirene_company_address" class="input-with-feedback form-control retrievedValue" value="` + entity.town + `" />
                </td>
            </tr>
            <tr>
                <td>
                    <label style="display: block;">${__("Country")}</label>
                </td>
                <td>
                    <input class="input-with-feedback form-control currentValue" value="` + AddressDoc.country + `"/>
                </td>
                <td class="center">` + sirenePrintCheckbox('company_country', checkValue([
      {fname: 'company_country', dval: AddressDoc.country, sval: entity.country}
    ])) + `</td>
                <td>
                    <input id="sirene_company_address" class="input-with-feedback form-control retrievedValue" value="` + entity.country + `" />
                </td>
            </tr>
            <tr>
                <td>
                    <label style="display: block;">${__("SIREN")}</label>
                </td>
                <td>
                    <input class="input-with-feedback form-control currentValue" value="` + currentDoc.siren + `"/>
                </td>
                <td>` + sirenePrintCheckbox('company_siren', checkValue([
      {fname: 'company_siren', dval: currentDoc.siren, sval: entity.siren}
    ])) + `</td>
                <td>
                    <input id="sirene_company_siren" class="input-with-feedback form-control retrievedValue" value="` + entity.siren + `" />
                </td>
            </tr>
            <tr>
                <td>
                    <label style="display: block;">${__("SIRET")}</label>
                </td>
                <td>
                    <input class="input-with-feedback form-control currentValue" value="` + currentDoc.siret + `"/>
                </td>
                <td>` + sirenePrintCheckbox('company_siret', checkValue([
      {fname: 'company_siret', dval: currentDoc.siret, sval: entity.siret}
    ])) + `</td>
                <td>
                    <input id="sirene_company_siret" class="input-with-feedback form-control retrievedValue" value="` + entity.siret + `"/>
                </td>
            </tr>
            <tr>
                <td>
                    <label style="display: block;">${__("NAF")}</label>
                </td>
                <td>
                    <input class="input-with-feedback form-control currentValue" value="` + currentDoc.code_naf + `"/>
                </td>
                <td>` + sirenePrintCheckbox('company_naf', checkValue([
      {fname: 'company_naf', dval: currentDoc.code_naf, sval: entity.code_naf}
    ])) + `</td>
                <td>
                    <input id="sirene_company_naf" class="input-with-feedback form-control retrievedValue" value="` + entity.code_naf + `" />
                </td>
            </tr>
            <tr>
                <td>
                    <label style="display: block;">${__("Tax ID")}</label>
                </td>
                <td>
                    <input class="input-with-feedback form-control currentValue" value="` + currentDoc.tax_id + `"/>
                </td>
                <td>` + sirenePrintCheckbox('company_vat_intra', checkValue([
      {fname: 'company_naf', dval: currentDoc.tax_id, sval: entity.tax_id}
    ])) + `</td>
                <td>
                    <input id="sirene_company_vat_intra" class="input-with-feedback form-control retrievedValue" value="` + entity.tax_id + `" />
                </td>
            </tr>
            <tr>
                <td>
                    <label style="display: block;">${__("Legal Form")}</label>
                </td>
                <td>
                    <input class="input-with-feedback form-control currentValue" value="` + currentDoc.legal_form + `"/>
                </td>
                <td>` + sirenePrintCheckbox('company_judicial_form', checkValue([
      {fname: 'company_judicial_form', dval: currentDoc.legal_form, sval: entity.legal_form}
    ])) + `</td>
                <td>
                    <input id="sirene_company_judicial_form" class="input-with-feedback form-control retrievedValue" value="` + entity.legal_form + `" />
                </td>
            </tr>
        </tbody>
    </table>
</div>
`
}

function sirenePrintCheckbox(field_name, match) {

  let result = '<span id="sirene_match_' + field_name + '" style="' + (match ? "display: block;" : "display: none;") + '" title="' + __("SireneIconCheckHelp") + '">' + "\n";
  result += '<svg class="es-icon ml-0 icon-sm" ><use href="#icon-solid-success"></use></svg>' + "\n";
  result += '</span>' + "\n";
  result += '<span id="sirene_mismatch_' + field_name + '" style="' + (match ? "display: none;" : "display: block;") + '" class="nowrap sirene_check">' + "\n";
  result += '<svg class="es-icon ml-0 icon-sm" style="display:inline-block"><use href="#icon-solid-error"></use></svg></i>' + "\n";
  result += '<button class="text-muted btn btn-default prev-doc addRemoveArrow icon-btn " data-field="' + field_name + '" data-direction="left" style="display:inline-block" title="' + __("SireneIconUpdateHelp") + '" data-original-title="' + __("SireneIconUpdateHelp") + '">' + "\n";
  result += '<svg class="es-icon es-line  icon-sm" style="" aria-hidden="true">' + "\n";
  result += '<use href="#es-line-left-chevron"></use>' + "\n";
  result += '</svg>' + "\n";
  result += '</button>' + "\n";
  result += '<input type="hidden" name="sirene_update_' + field_name + '" value="0">' + "\n";
  result += '</span>' + "\n";

  return result;
}

const FIELD_MAPPING = {
  'company_address': {doctype: 'Address', field: 'address_line1'},
  'company_city': {doctype: 'Address', field: 'city'},
  'company_pincode': {doctype: 'Address', field: 'pincode'},
  'company_country': {doctype: 'Address', field: 'country'},
};

function separateAndMapFields(fields, baseDoctype) {
  const doctypeFields = {};
  const addressFields = {};

  for (const [fieldName, value] of Object.entries(fields)) {
    if (FIELD_MAPPING[fieldName]) {
      const mapping = FIELD_MAPPING[fieldName];

      if (mapping.doctype === 'Address') {
        addressFields[mapping.field] = value;
      } else if (mapping.doctype === baseDoctype) {
        doctypeFields[mapping.field] = value;
      }
    } else {
      doctypeFields[fieldName] = value;
    }
  }

  return {doctypeFields, addressFields};
}

async function collectSelectedFields() {
  const fields = {};
  const fieldPromises = [];

  $(".updateFields").find("tr").each((index, element) => {
    if ($(element).find(".currentValue").data('updated')) {
      const fieldName = $(element).find(".addRemoveArrow").data('field');
      const value = $(element).find(".retrievedValue").val();

      const fieldPromise = (async () => {
        if (fieldName === 'code_naf') {
          fields[fieldName] = await getCodeNaf(value);
        } else if (fieldName === 'legal_form') {
          fields[fieldName] = await getLegalForm(value);
        } else {
          fields[fieldName] = value;
        }
      })();

      fieldPromises.push(fieldPromise);
    }
  });

  await Promise.all(fieldPromises);
  return fields;
}

async function updateFieldsWithSireneInfo(frm, doctype) {
  try {
    const allFields = await collectSelectedFields();

    if (Object.keys(allFields).length === 0) {
      frappe.msgprint(__('No fields selected for update'));
      return;
    }

    const {doctypeFields, addressFields} = separateAndMapFields(allFields, doctype);

    frappe.dom.freeze(__('Updating data...'));

    if (Object.keys(doctypeFields).length > 0) {
      await updateDoctype(doctype, frm.doc.name, doctypeFields);
    }

    if (Object.keys(addressFields).length > 0) {
      const addressName = doctype === 'Customer'
        ? frm.doc.customer_primary_address
        : frm.doc.supplier_primary_address;

      if (addressName) {
        await updateDoctype('Address', addressName, addressFields);
      } else {
        frappe.show_alert({
          message: __('Warning: No primary address to update'),
          indicator: 'orange'
        }, 5);
      }
    }

    await frm.reload_doc();

    frappe.show_alert({
      message: doctype === "Customer"
        ? __('Customer successfully updated')
        : __('Supplier successfully updated'),
      indicator: 'green'
    });

  } catch (error) {
    console.error('Error:', error);
    frappe.msgprint({
      title: __('Error'),
      indicator: 'red',
      message: __('Error while updating: ') + (error.message || error)
    });
  } finally {
    frappe.dom.unfreeze();
  }
}

async function getAddressDoctype(currentDoc) {
  let doctypeMethod = currentDoc.doctype === 'Customer' ? 'frappe.client.get' : 'frappe.client.get'
  let doctypePrimaryAddress = currentDoc.doctype === 'Customer' ? currentDoc.customer_primary_address : currentDoc.supplier_primary_address
  return new Promise((resolve, reject) => {
    frappe.call({
      method: doctypeMethod,
      args: {
        doctype: 'Address',
        name: doctypePrimaryAddress
      },
      callback: function (r) {
        if (r.message) {
          resolve(r.message);
        } else {
          resolve(null);
        }
      },
      error: function (r) {
        console.log('Error:', r);
        frappe.throw(__(r));
        reject(r);
      }
    });
  });
}

function checkValue(datas) {
  let match = true;
  $.map(datas, function (item, idx) {
    match &&= item.dval.localeCompare(item.sval, "fr", {sensitivity: "accent"}) === 0;
  });
  return match;
}

function leftFillNum(num, targetLength) {
  return num.toString().padStart(targetLength, "0");
}
