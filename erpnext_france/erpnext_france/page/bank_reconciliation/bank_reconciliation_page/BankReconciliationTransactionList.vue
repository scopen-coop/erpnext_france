<template>
	<div class="transactions-table">
		<div class="text-center">
			<div class="text-center section-title">
				<h4>{{ __("Bank Transactions") }}</h4>
			</div>
			<div>
				<div class="btn-group" role="group" aria-label="...">
					<button
						v-for="(filter, i) in [{ value: 'All', label: __('All') }, { value: 'Unreconciled', label: __('Unreconciled') }, { value: 'Reconciled', label: __('Reconciled') }]"
						:key="i" type="button" class="btn btn-default" :class="list_filter == filter.value ? 'active' : ''"
						@click="change_filter(filter)">
						{{ filter.label }}
					</button>
				</div>
			</div>
		</div>
		<div class="transactions-table">
			<div ref="transactionslist"></div>
		</div>
		<div class="text-center document-options">
			<div class="btn-group" role="group" aria-label="Bank Transactions Options">
				<button type="button" class="btn btn-default" @click="auto_reconciliation">{{ __("Automatic reconciliation")
				}}</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { TabulatorFull as Tabulator } from 'tabulator-tables';

const props = defineProps({
	bank_account: {
		type: String,
		default: null
	},
	start_date: {
		type: String,
		default: null
	},
	end_date: {
		type: String,
		default: null
	},
	selected_transactions: {
		type: Array,
		default: () => []
	}
})

const transactionslist = ref(null);
const tabulator = ref(null);
const tableData = ref([]);
const list_filter = ref("Unreconciled")

function get_transaction_list() {
	if (props.bank_account && props.start_date && props.end_date) {
		const query_filters = [
			["Bank Transaction", "bank_account", "=", props.bank_account],
			["Bank Transaction", "date", "between", [props.start_date, props.end_date]],
			["Bank Transaction", "docstatus", "=", 1]
		]

		if (list_filter.value == "Unreconciled") {
			query_filters.push(["Bank Transaction", "unallocated_amount", "!=", 0])
		} else if (list_filter.value == "Reconciled") {
			query_filters.push(["Bank Transaction", "unallocated_amount", "=", 0])
		}

		return frappe.xcall('frappe.client.get_list', {
			doctype: "Bank Transaction",
			order_by: "date DESC",
			fields: ["name", "date", "currency", "debit", "credit", "description", "allocated_amount", "unallocated_amount", "bank_account"],
			filters: query_filters,
			limit_page_length: 500,
			limit_start: 0
		}).then(r => {
			const mapped_transactions = r.map(transaction => ({
				...transaction,
				amount: transaction.unallocated_amount,
				link: `/app/Form/Bank Transaction/${transaction.name}`
			}))

			tableData.value = mapped_transactions;
		})
	}
}

function change_filter(filter) {
	list_filter.value = filter.value;
	get_transaction_list()
}

function auto_reconciliation() {
	frappe.show_alert({ message: __(`Automatic reconciliation in progress`), indicator: "green" })
	frappe.xcall('erpnext.accounts.page.bank_reconciliation.auto_bank_reconciliation.auto_bank_reconciliation',
		{ bank_transactions: tableData.value }
	).then(() => {
		get_transaction_list()
	})
}

const emit = defineEmits(['transactionsChange'])
function onSelectedRowsChange() {
	var selectedData = tabulator.value.getSelectedData();
	emit('transactionsChange', selectedData)
}

const columns = [
	{
		formatter: "rowSelection", titleFormatter: "rowSelection", titleFormatterParams: {
			rowRange: "active"
		}, hozAlign: "center", headerSort: false
	},
	{
		title: __("Date"), field: "date", formatter: function (cell, formatterParams, onRendered) {
			const cellValue = cell.getValue();

			if (!cellValue) {
				return null;
			}

			return frappe.datetime.str_to_user(cellValue)
		},
	},
	{ title: __("Description"), field: "description", width: "60px", formatter: "html", headerFilter:"input" },
	{
		title: __("Amount"), field: "amount", formatter: function (cell, formatterParams, onRendered) {
			const cellValue = cell.getValue();
			const row = cell.getRow();
			const cellRowData = row.getData();

			if (!cellValue) {
				return null;
			}

			return format_currency(cellValue, cellRowData.currency)
		},
	},
	{
		title: __("Link"), field: 'link', formatter: function (cell, formatterParams, onRendered) {
			const cellValue = cell.getValue();

			if (!cellValue) {
				return null;
			}

			return `<a href="${cellValue}" target="_blank"><i class='uil uil-external-link-alt'></i></a>`
		}
	}
]

onMounted(() => {
	tabulator.value = new Tabulator(transactionslist.value, {
		data: tableData.value,
		columns: columns,
		selectable: true,
		pagination: true,
		paginationSize: 20,
		paginationSizeSelector: [10, 20, 50, 100, true],
		placeholder: __("No data available for this period"),
		locale: true,
		langs: {
			"default": {
				"pagination": {
					"page_size": __("Page Size"),
					"page_title": __("Show Page"),
					"first": __("First"),
					"first_title": __("First Page"),
					"last": __("Last"),
					"last_title": __("Last Page"),
					"prev": __("Prev"),
					"prev_title": __("Prev Page"),
					"next": __("Next"),
					"next_title": __("Next Page"),
					"all": __("All"),
					"counter": {
						"showing": __("Showing"),
						"of": __("of"),
						"rows": __("rows"),
						"pages": __("pages"),
					}
				},
			}
		},
	});

	tabulator.value.on("rowSelectionChanged", function (data, rows, selected, deselected) {
		onSelectedRowsChange()
	});

	get_transaction_list()
})

watch(() => [props.bank_account, props.start_date, props.end_date], () => {
	get_transaction_list()
});

watch(tableData, (newData, oldData) => {
	tabulator.value.replaceData(newData);
})

defineExpose({
	get_transaction_list
})

</script>

<style lang='scss'>
.transactions-table {
	margin-bottom: 50px;
	margin-top: 1rem;

	.section-title {
		border-bottom: 1px solid #d1d8dd;
		margin-bottom: 10px;
		text-transform: uppercase;
	}
}

.no-data {
	margin: 25px;
	height: 150px;
}
</style>
