// Copyright (c) 2020, Dokos and Contributors
// License: See license.txt

erpnext.journalAdjustment = class AccountingJournalAdjustment {
	constructor(opts) {
		Object.assign(this, opts);
		this.make()
	}

	make() {
		const me = this;
		this.dialog = new frappe.ui.Dialog({
			title: __('Adjust the accounting journal'),
			fields: [
				{
					"label" : "Current Journal",
					"fieldname": "current_journal",
					"fieldtype": "HTML"
				},
				{
					"label" : "New Accounting Journal",
					"fieldname": "new_journal",
					"fieldtype": "Link",
					"options": "Accounting Journal",
					"reqd": 1
				}
			],
			primary_action: function() {
				frappe.xcall('erpnext_france.erpnext_france.doctype.accounting_journal.accounting_journal.accounting_journal_adjustment', {
					doctype: me.doctype,
					docnames: me.docnames,
					accounting_journal: me.dialog.get_values().new_journal
				}).then(() => {
					frappe.show_alert({message: __('Accounting Journal adjustment in progress'), indicator: 'green'})
				})
				me.dialog.hide()
			},
			primary_action_label: __('Submit')
		})

		this.get_accounting_entries()
	}

	get_accounting_entries() {
		frappe.xcall('erpnext_france.erpnext_france.doctype.accounting_journal.accounting_journal.get_entries', {
			doctype: this.doctype,
			docnames: this.docnames
		}).then(r => {
			if (r && r.length) {
				const rows = r.map(f => `
					<tr>
						<th scope="row">${f.voucher_no}</th>
						<th>${f.account}</th>
						<td>${format_currency(f.debit, f.account_currency)}</td>
						<td>${format_currency(f.credit, f.account_currency)}</td>
						<td>${f.accounting_journal || ""}</td>
					</tr>
				`).join("")

				const table = `
					<table class="table">
						<thead>
						<tr>
							<th scope="col">${__("Document")}</th>
							<th scope="col">${__("Account")}</th>
							<th scope="col">${__("Debit")}</th>
							<th scope="col">${__("Credit")}</th>
							<th scope="col">${__("Accounting Journal")}</th>
						</tr>
						</thead>
						<tbody>
							${rows}
						</tbody>
					</table>
				`
				this.dialog.fields_dict.current_journal.$wrapper.html(table);
				this.dialog.show()
			} else {
				frappe.msgprint({
					message: __("No corresponding general ledger entries found for this document"),
					title: __("Accounting journal not found")
				})
			}
		})
	}
}