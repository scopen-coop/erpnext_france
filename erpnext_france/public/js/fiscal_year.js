// Copyright (c) 2017, Britlog and contributors
// For license information, please see license.txt

frappe.ui.form.on("Fiscal Year Company", "export_fec", function(frm,cdt,cdn) {
    var doc = frappe.get_doc(cdt, cdn);
//    frappe.msgprint(frm.doc.name);

    //Create a form to place the HTML content
    var formData = new FormData();

    //Push the HTML content into an element
    formData.append("company_name", doc.company);
    formData.append("fiscal_year", frm.doc.name);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", '/api/method/erpnext_france.fec.export.export_csv');
    xhr.setRequestHeader("X-Frappe-CSRF-Token", frappe.csrf_token);
    xhr.responseType = "text";

    xhr.onload = function(success) {
        if (this.status === 200) {
            var filename = "";
            var disposition = xhr.getResponseHeader('Content-Disposition');

            if (disposition) {
                var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                var matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
            }
            var type = xhr.getResponseHeader('Content-Type');
            var blob = new Blob([success.currentTarget.response], {type: type });

            var URL = window.URL || window.webkitURL;
            var downloadUrl = URL.createObjectURL(blob);

            if (filename) {
                // use HTML5 a[download] attribute to specify filename
                var a = document.createElement("a");
                // safari doesn't support this yet
                if (typeof a.download === 'undefined') {
                    window.location = downloadUrl;
                } else {
                    a.href = downloadUrl;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                }
            } else {
                window.location = downloadUrl;
            }
        }
    };
    xhr.send(formData);

});