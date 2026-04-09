frappe.listview_settings["Sales Invoice"] = frappe.listview_settings["Sales Invoice"] || {};

const _onload = frappe.listview_settings["Sales Invoice"].onload;

frappe.listview_settings["Sales Invoice"].onload = function (listview) {
  if (typeof _onload === "function") _onload(listview);
  listview.page.add_action_item(__("Générer lignes de bordereau"), function () {
    const selected_items = listview.get_checked_items();
    if (!selected_items.length) return;

    const invoice_names = selected_items.map((item) => item.name);

    frappe.call({
      method: "erpnext_france.regional.france.sepa_utils.add_invoices_to_sepa_bordereau_bulk", args: {
        invoice_names, invoice_type: "Sales Invoice",
      }, freeze: true, callback: function (r) {
        if (r.message) {
          show_sepa_summary_report(r.message);
          listview.refresh();
        }
      },
    });
  });
};

function show_sepa_summary_report(report) {
  let message = `<h4>${__("Summary Report")}</h4>`;
  message += `<p><b>${__("Success")}:</b> ${report.success.length}</p>`;
  message += `<p><b>${__("Failed")}:</b> ${report.failed.length}</p>`;

  if (report.failed.length > 0) {
    message += `<hr><h5>${__("Details of Failures")}</h5><div style="max-height: 200px; overflow-y: auto;"><ul>`;
    report.failed.forEach((item) => {
      message += `<li><b>${item.name}:</b> ${item.reason}</li>`;
    });
    message += `</ul></div>`;
  }

  frappe.msgprint({
    title: __("SEPA Bulk Generation"), message, indicator: report.failed.length > 0 ? "orange" : "green", wide: true,
  });
}
