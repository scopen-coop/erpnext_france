// Copyright (c) 2021, Britlog and contributors
// For license information, please see license.txt

frappe.ui.form.on("ERPNext France Settings", {
  refresh: function (frm) {
    frappe
      .call(
        "erpnext_france.utils.create_down_payment_item.has_down_payment_item"
      )
      .then((r) => {
        if (r.message) {
          return;
        }
        frm.add_custom_button(
          __("ERPNext France - Create Down Payment Item"),
          function () {
            display_dialog_create_down_payment_item(
              frm,
              frappe.defaults.get_user_default("Company")
            );
          },
          __("Manage")
        );
      });
    frm.add_custom_button(
      __("ERPNext France - Update companies (sirene)"),
      function () {
        display_dialog_update_companies(
          frm,
          frappe.defaults.get_user_default("Company")
        );
      },
      __("Manage")
    );
  },
});

async function display_dialog_update_companies() {

  const updateReport = await frappe.call({
    freeze: true,
    freeze_message: __("Retrieving data..."),
    method:
      "erpnext_france.controllers.fetch_company_from_sirene.execute_sirene_check",
    callback: function (response) {
      if (!response || !response.message) {
        frappe.throw(__("No Response From Server"));

      }
    },
  });

  let updates = updateReport.message.updates
  let dialog = new frappe.ui.Dialog({
    title: __("ERPNext France - Update companies (sirene)"),
    fields: [
      {
        fieldname: 'table_Customer_section',
        fieldtype: 'Section Break',
      },
      {
        fieldname: "Customer",
        fieldtype: "Table",
        label: __("Customer(s)"),
        cannot_add_rows: true,
        cannot_delete_rows: true,
        in_place_edit: true,
        hide_footer: true,
        data: updates.Customer ? updates.Customer.map(item => ({
          ...item,
          status: 'Differences detected'
        })) : [],
        fields: [
          {
            fieldname: "display_name",
            label: __("Name"),
            fieldtype: "Data",
            in_list_view: 1,
            read_only: 1,
            columns: 4,
            options: "Customer",
          },
          {
            fieldname: "status_Customer",
            label: __("Status"),
            fieldtype: "Data",
            in_list_view: 1,
            read_only: 1,
            columns: 2
          }
        ],
      },
      {
        fieldname: 'table_Customer_buttons',
        fieldtype: 'HTML'
      },
      {
        fieldname: 'table_Supplier_section',
        fieldtype: 'Section Break',
      },
      {
        fieldname: "Supplier",
        fieldtype: "Table",
        label: __("Supplier(s)"),
        cannot_add_rows: true,
        cannot_delete_rows: true,
        in_place_edit: true,
        data: updates.Supplier ? updates.Supplier.map(item => ({
          ...item,
          status: 'Differences detected',
        })) : [],
        fields: [
          {
            fieldname: "display_name",
            label: __("Name"),
            fieldtype: "Data",
            in_list_view: 1,
            read_only: 1,
            columns: 4,
          },
          {
            fieldname: "status_Supplier",
            label: __("Status"),
            fieldtype: "Data",
            in_list_view: 1,
            read_only: 1,
            columns: 2
          }
        ],
      },
      {
        fieldname: 'table_Supplier_buttons',
        fieldtype: 'HTML'
      }
    ],
    size: "large", // small, large, extra-large
    onhide: function () {
      this.$wrapper.remove();
      dialog = null;
    },
    primary_action_label: __("Close"),
    async primary_action() {
      dialog.hide()
    },
    async secondary_action() {

    },
  });

  dialog.fields_dict.table_Customer_buttons.$wrapper.html(`
    <div style="margin: -20px 0 30px;">
        <button class="btn btn-primary btn-sm" id="btn-table-Customer-action">
            ${__('Update')}
        </button>
    </div>
`);

  dialog.fields_dict.table_Supplier_buttons.$wrapper.html(`
    <div style="margin: -20px 0 30px;">
        <button class="btn btn-primary btn-sm" id="btn-table-Supplier-action">
            ${__('Update')}
        </button>
    </div>
`);


  setTimeout(() => {
    let grid = dialog.fields_dict.Supplier.grid;
    grid.get_selected_children = function () {
      return this.grid_rows
        .filter(row => {
          let $checkbox = row.row_check.find('input[type="checkbox"]');
          return $checkbox.hasClass('grid-row-check') && $checkbox.prop('checked');
        })
        .map(row => row.doc);
    };

    /*dialog.fields_dict.Customer.grid.grid_rows.forEach((row) => {
      format_status("Customer", row);
    });
    dialog.fields_dict.Supplier.grid.grid_rows.forEach((row) => {
      format_status("Supplier", row);
    });*/

    const grid_customer = dialog.fields_dict.Customer.grid;
    const grid_supplier = dialog.fields_dict.Supplier.grid;


    function make_grid_clickable(grid, doctype) {
      grid.grid_rows.forEach((row) => {
        format_status(doctype, row);

        const name_cell = row.columns.name;
        if (name_cell) {
          $(name_cell.static_area).css({
            'color': 'var(--primary-color)',
            'cursor': 'pointer',
            'font-weight': '500'
          });

          $(name_cell.static_area).show();
          $(name_cell.wrapper).find('.like_disabled-input').hide();
        }
      });

      grid.wrapper.find('.grid-body')[0].addEventListener('click', function (e) {
        const $target = $(e.target);
        const $row = $target.closest('.grid-row');

        if ($row.length) {
          const row_index = $row.index();
          const row_data = grid.grid_rows[row_index];

          const $cell = $target.closest('.col');
          const is_name_column = $cell.find('[data-fieldname="name"]').length > 0 ||
            $target.closest('[data-fieldname="name"]').length > 0 ||
            $cell.index() === 2;

          if (is_name_column) {
            const doc_name = row_data?.doc?.name;

            if (doc_name) {
              e.preventDefault();
              e.stopPropagation();
              e.stopImmediatePropagation();

              window.open(`/app/${doctype.toLowerCase()}/${encodeURIComponent(doc_name)}`, '_blank');
              return false;
            }
          }
        }
      }, true);
    }

    make_grid_clickable(grid_customer, 'Customer');
    make_grid_clickable(grid_supplier, 'Supplier');


  }, 100);
  dialog.show()


  dialog.$wrapper.find('#btn-table-Customer-action').on('click', function () {
    update_rows(dialog, "Customer")
  });
  dialog.$wrapper.find('#btn-table-Supplier-action').on('click', function () {
    update_rows(dialog, "Supplier")
  });

}

async function update_rows(dialog, doctype) {

  let selected_rows = dialog.fields_dict[doctype].grid.get_selected_children();

  if (selected_rows.length === 0) {
    let $table_wrapper = dialog.fields_dict[doctype].$wrapper
    $table_wrapper.append(`
            <div class="alert alert-warning alert-dismissible fade show" role="alert" style="margin-bottom: 10px;">${__('Please select at least one line')}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
        `);

    setTimeout(function () {
      $table_wrapper.find('.alert').fadeOut(300, function () {
        $(this).remove();
      });
    }, 5000);
    return;
  }

  frappe.dom.freeze(__("Updating data..."));
  try {
    for (const row of selected_rows) {
      update_status(doctype, dialog, row, 'In Progress');
      let response = await update_doc_with_sirene_info(row.current_data, row.new_data, doctype)
      if (response.name)
        update_status(doctype, dialog, row, 'Updated');
      else
        update_status(doctype, dialog, row, 'Error');

    }

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
}

function format_status(doctype, grid_row) {
  let status = grid_row.doc.status;
  let $cell = $(grid_row.row).find(`[data-fieldname="status_${doctype}"]`);
  let configs = {
    'Differences detected': {class: 'orange', text: __('Differences detected')},
    'In Progress': {class: 'blue', text: __('In Progress')},
    'Updated': {class: 'green', text: __('Updated')},
    'Error': {class: 'red', text: __('Error')}
  };

  let config = configs[status];
  if (config) {
    $cell.html(`
          <span class="indicator-pill ${config.class}">

              ${config.text}
          </span>
      `);
  }
}

function update_status(doctype, dialog, row, new_status) {
  row.status = new_status;
  let grid_row = dialog.fields_dict[doctype].grid.grid_rows.find(
    gr => gr.doc.name === row.name || gr.doc === row
  );

  if (grid_row) {
    grid_row.doc.status = new_status;
    format_status(doctype, grid_row);
    if (new_status === 'Updated' || new_status === 'In Progress') {
      let $checkbox = grid_row.row_check.find('input[type="checkbox"]')
        .prop('disabled', true)
        .prop('checked', false);
      grid_row.doc.__checked = 0;
      $(grid_row.row).removeClass('highlight');
      $checkbox.removeClass('grid-row-check');

    }
  }
}
