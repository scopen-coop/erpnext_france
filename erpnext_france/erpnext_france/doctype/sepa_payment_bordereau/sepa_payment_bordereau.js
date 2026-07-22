// Copyright (c) 2026, Scopen and contributors
// For license information, please see license.txt

function company_bank_account_filters(company) {
  return {
    company: company,
    is_company_account: 1,
    party_type: ["in", ["", null]],
    party: ["in", ["", null]],
  };
}

function set_default_bank_account(frm) {
  if (!frm.doc.company || frm.doc.bank_account) {
    return;
  }

  frappe.db.get_value(
    "Company",
    frm.doc.company,
    "default_bank_account",
    function (company) {
      const filters = company_bank_account_filters(frm.doc.company);

      if (company && company.default_bank_account) {
        frappe.db
          .get_list("Bank Account", {
            filters: { ...filters, account: company.default_bank_account },
            fields: ["name", "party_type", "party"],
            limit: 5,
          })
          .then((rows) => {
            const company_bank = (rows || []).find(
              (row) => !row.party_type && !row.party
            );
            if (company_bank) {
              frm.set_value("bank_account", company_bank.name);
            } else {
              set_fallback_company_bank_account(frm, filters);
            }
          });
      } else {
        set_fallback_company_bank_account(frm, filters);
      }
    }
  );
}

function set_fallback_company_bank_account(frm, filters) {
  frappe.db
    .get_list("Bank Account", {
      filters: { ...filters, is_default: 1 },
      fields: ["name", "party_type", "party"],
      limit: 5,
    })
    .then((rows) => {
      const company_bank = (rows || []).find(
        (row) => !row.party_type && !row.party
      );
      if (company_bank) {
        frm.set_value("bank_account", company_bank.name);
      }
    });
}

function is_valid_company_bank_account(bank, company) {
  return (
    bank &&
    bank.is_company_account &&
    !bank.party_type &&
    !bank.party &&
    bank.company === company
  );
}

function ensure_company_bank_account(frm, show_alert = true) {
  if (!frm.doc.bank_account || !frm.doc.company) {
    return;
  }

  frappe.db.get_value(
    "Bank Account",
    frm.doc.bank_account,
    ["is_company_account", "party_type", "party", "company"],
    function (r) {
      if (is_valid_company_bank_account(r, frm.doc.company)) {
        return;
      }

      frm.set_value("bank_account", null);
      set_default_bank_account(frm);

      if (show_alert) {
        frappe.show_alert({
          message: __(
            "Customer/supplier bank account replaced with company bank account"
          ),
          indicator: "orange",
        });
      }
    }
  );
}

function get_line_types(payment_type) {
  if (payment_type === "Credit") {
    return { invoice_type: "Purchase Invoice", party_type: "Supplier" };
  }
  return { invoice_type: "Sales Invoice", party_type: "Customer" };
}

function is_line_locked(line) {
  return Boolean(line.payment_entry) || ["Accepted", "Rejected"].includes(line.status);
}

function is_status_locked(line) {
  return line.status === "Accepted";
}

function set_grid_field_read_only(grid_row, fieldname, read_only) {
  if (!grid_row) {
    return;
  }

  if (typeof grid_row.toggle_editable === "function") {
    grid_row.toggle_editable(fieldname, !read_only);
    return;
  }

  if (grid_row.on_grid_fields_dict && grid_row.on_grid_fields_dict[fieldname]) {
    const field = grid_row.on_grid_fields_dict[fieldname];
    field.df.read_only = read_only ? 1 : 0;
    if (typeof field.refresh === "function") {
      field.refresh();
    }
  }

  if (
    grid_row.grid_form &&
    grid_row.grid_form.fields_dict &&
    grid_row.grid_form.fields_dict[fieldname]
  ) {
    const form_field = grid_row.grid_form.fields_dict[fieldname];
    form_field.df.read_only = read_only ? 1 : 0;
    if (typeof form_field.refresh === "function") {
      form_field.refresh();
    }
  }
}

function lock_processed_lines(frm) {
  const grid = frm.fields_dict.lines && frm.fields_dict.lines.grid;
  if (!grid) {
    return;
  }

  const data_fields = ["invoice", "party", "amount", "mandate"];

  (frm.doc.lines || []).forEach((line) => {
    if (!line.name) {
      return;
    }

    const grid_row = grid.grid_rows_by_docname[line.name];
    if (!grid_row) {
      return;
    }

    const data_locked = is_line_locked(line);
    data_fields.forEach((fieldname) => {
      set_grid_field_read_only(grid_row, fieldname, data_locked);
    });

    // Pending / Rejected: status (and rejection reason) remain editable
    set_grid_field_read_only(grid_row, "status", is_status_locked(line));
    set_grid_field_read_only(
      grid_row,
      "rejection_reason",
      line.status === "Accepted"
    );

    if (grid_row.wrapper) {
      grid_row.wrapper
        .find(".grid-delete-row, .grid-duplicate-row")
        .toggle(!data_locked);
    }
  });
}

function sync_line_types(frm, cdt, cdn) {
  const { invoice_type, party_type } = get_line_types(frm.doc.payment_type);
  frappe.model.set_value(cdt, cdn, "invoice_type", invoice_type);
  frappe.model.set_value(cdt, cdn, "party_type", party_type);
}

frappe.ui.form.on("SEPA Payment Bordereau", {
  refresh: function (frm) {
    if (frm.doc.status === "Draft") {
      ensure_company_bank_account(frm, false);
    }

    lock_processed_lines(frm);
    // Grid rows may finish rendering after refresh
    setTimeout(() => lock_processed_lines(frm), 200);

    // Add Validate button
    if (
      frm.doc.status === "Draft" &&
      frm.doc.lines &&
      frm.doc.lines.length > 0
    ) {
      frm
        .add_custom_button(__("Validate Bordereau"), function () {
          frappe.call({
            method: "validate_bordereau",
            doc: frm.doc,
            callback: function (r) {
              frm.reload_doc();
            },
          });
        })
        .addClass("btn-primary");
    }

    // Add Generate SEPA File button
    if (frm.doc.status === "Validated" || frm.doc.status === "Exported") {
      frm
        .add_custom_button(__("Generate SEPA File"), function () {
          frappe.call({
            method: "generate_sepa_file",
            doc: frm.doc,
            callback: function (r) {
              if (r.message) {
                frappe.msgprint(__("SEPA file generated: {0}", [r.message]));
                frm.reload_doc();
              }
            },
          });
        })
        .addClass("btn-primary");
    }

    // Add Download SEPA File button when a file is already generated
    if (frm.doc.sepa_file) {
      frm.add_custom_button(__("Download SEPA File"), function () {
        const download_url = `/api/method/frappe.utils.file_manager.download_file?file_url=${encodeURIComponent(
          frm.doc.sepa_file
        )}`;
        window.location.href = download_url;
      });
    }

    // Add Mark as Sent button
    if (frm.doc.status === "Exported") {
      frm.add_custom_button(__("Mark as Sent"), function () {
        frappe.call({
          method: "mark_as_sent",
          doc: frm.doc,
          callback: function (r) {
            frm.reload_doc();
          },
        });
      });
    }

    // Accept selected pending lines after bank execution
    if (["Sent", "Partial Rejections", "Exported"].includes(frm.doc.status)) {
      const has_pending_lines = (frm.doc.lines || []).some(
        (line) => line.status === "Pending"
      );
      if (has_pending_lines) {
        frm.add_custom_button(
          __("Accept Selection"),
          function () {
            accept_selected_lines(frm);
          },
          __("Actions")
        );
      }
    }

    // Set color indicator based on status
    if (frm.doc.status) {
      var color_map = {
        Draft: "gray",
        Validated: "blue",
        Exported: "orange",
        Sent: "purple",
        "Partial Rejections": "red",
        Closed: "green",
      };
      frm.page.set_indicator(frm.doc.status, color_map[frm.doc.status]);
    }
  },

  payment_type: function (frm) {
    frm.trigger("set_naming");
    frm.trigger("setup_line_queries");
  },

  lines_add: function (frm, cdt, cdn) {
    sync_line_types(frm, cdt, cdn);
  },

  onload: function (frm) {
    frm.trigger("setup_line_queries");
    frm.trigger("setup_bank_account_query");
    if (frm.doc.bank_account) {
      ensure_company_bank_account(frm);
    } else {
      set_default_bank_account(frm);
    }
  },

  company: function (frm) {
    frm.set_value("bank_account", null);
    frm.trigger("setup_bank_account_query");
    set_default_bank_account(frm);
  },

  setup_bank_account_query: function (frm) {
    if (!frm.doc.company) {
      return;
    }

    frm.set_query("bank_account", function () {
      return {
        filters: company_bank_account_filters(frm.doc.company),
      };
    });
  },

  set_naming: function (frm) {
    if (frm.doc.payment_type === "Debit") {
      frm.set_value("naming_series", "SEPA-DEBIT-.YYYY.-.####");
    } else if (frm.doc.payment_type === "Credit") {
      frm.set_value("naming_series", "SEPA-CREDIT-.YYYY.-.####");
    }
  },

  setup_line_queries: function (frm) {
    const { invoice_type, party_type } = get_line_types(frm.doc.payment_type);

    frm.set_query("invoice", "lines", function (doc, cdt, cdn) {
      const row = locals[cdt][cdn];
      row.invoice_type = invoice_type;
      row.party_type = party_type;

      const filters = {
        docstatus: 1,
        outstanding_amount: [">", 0],
      };
      if (frm.doc.company) {
        filters.company = frm.doc.company;
      }
      return { filters };
    });

    frm.set_query("party", "lines", function (doc, cdt, cdn) {
      const row = locals[cdt][cdn];
      row.invoice_type = invoice_type;
      row.party_type = party_type;
      return {};
    });
  },
});

function get_selected_grid_rows(frm, fieldname) {
  const grid = frm.fields_dict[fieldname].grid;
  if (grid.get_selected_children) {
    return grid.get_selected_children();
  }

  return (grid.grid_rows || [])
    .filter((row) => {
      const $checkbox = row.row_check.find('input[type="checkbox"]');
      return $checkbox.hasClass("grid-row-check") && $checkbox.prop("checked");
    })
    .map((row) => row.doc);
}

function accept_selected_lines(frm) {
  const selected = get_selected_grid_rows(frm, "lines");
  const pending = selected.filter((line) => line.status === "Pending");

  if (!pending.length) {
    frappe.msgprint(__("Please select at least one pending line"));
    return;
  }

  frappe.confirm(__("Accept {0} selected line(s)?", [pending.length]), () => {
    frappe.call({
      method: "accept_selected_lines",
      doc: frm.doc,
      args: {
        line_names: pending.map((line) => line.name),
      },
      freeze: true,
      freeze_message: __("Accepting selected lines..."),
      callback: function (r) {
        if (r.message) {
          show_accept_results(r.message);
        }
        frm.reload_doc();
      },
    });
  });
}

function show_accept_results(results) {
  const parts = [];

  if (results.success.length) {
    parts.push(`<b>${__("Accepted")}:</b> ${results.success.length}`);
  }
  if (results.skipped.length) {
    parts.push(`<b>${__("Skipped")}:</b> ${results.skipped.length}`);
  }
  if (results.failed.length) {
    parts.push(`<b>${__("Failed")}:</b> ${results.failed.length}`);
    results.failed.forEach((row) => {
      parts.push(`${row.invoice}: ${row.reason}`);
    });
  }

  frappe.msgprint({
    message: parts.join("<br>"),
    indicator: results.failed.length ? "orange" : "green",
  });
}

frappe.ui.form.on("SEPA Payment Bordereau Line", {
  form_render: function (frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (is_line_locked(row)) {
      lock_processed_lines(frm);
    }
  },

  invoice: function (frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (!row.invoice || is_line_locked(row)) {
      return;
    }

    sync_line_types(frm, cdt, cdn);

    const { invoice_type } = get_line_types(frm.doc.payment_type);
    const party_field =
      invoice_type === "Purchase Invoice" ? "supplier" : "customer";

    frappe.db.get_value(
      invoice_type,
      row.invoice,
      [party_field, "outstanding_amount"],
      (r) => {
        if (!r) {
          return;
        }
        frappe.model.set_value(cdt, cdn, "party", r[party_field]);
        frappe.model.set_value(cdt, cdn, "amount", r.outstanding_amount);

        if (frm.doc.payment_type === "Debit" && r[party_field]) {
          frappe.db.get_value(
            "Customer",
            r[party_field],
            "sepa_mandate",
            (customer) => {
              if (customer && customer.sepa_mandate) {
                frappe.model.set_value(
                  cdt,
                  cdn,
                  "mandate",
                  customer.sepa_mandate
                );
              }
            }
          );
        }
      }
    );
  },

  amount: function (frm) {
    frm.trigger("calculate_total");
  },

  lines_remove: function (frm) {
    frm.trigger("calculate_total");
  },
});
