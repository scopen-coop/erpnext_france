<template>
	<div v-show="props.transactions.length" class="matching-box">
		<div class="text-center">
			<div class="section-title">
					<h4>{{ __("Documents") }}</h4>
			</div>
			<div>
				<div class="btn-group" role="group" aria-label="Document Options">
					<button
						v-for="(dt, i) in Object.keys(matching_documents)"
						:key="i"
						type="button"
						class="btn btn-default"
						:class="document_type==dt ? 'active': ''"
						@click="change_doctype(dt)">
							{{ __(dt)}}
					</button>
				</div>
			</div>
		</div>
		<div class="documents-table">
			<div ref="matchingbox"></div>
		</div>
		<div v-show="tableData.length || (props.transactions.length && !tableData.length)" class="text-center document-options">
			<div class="btn-group" role="group" aria-label="Document Options">
				<button type="button" class="btn btn-default" @click="get_linked_docs(false)">{{ __("Show the full list") }}</button>
				<button type="button" class="btn btn-primary" @click="create_new_document">{{ __("Create a new {0}", [__(document_type)]) }}</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import {ref, onMounted, watch} from 'vue'
import { TabulatorFull as Tabulator } from 'tabulator-tables';

const props = defineProps({
	transactions: {
		type: Array,
		default: () => []
	}
})

const matchingbox = ref(null);
const tabulator = ref(null);
const tableData = ref([]);

const document_type = ref("Payment Entry");

const columns = [
	{
		formatter: "rowSelection", titleFormatter: "rowSelection", titleFormatterParams: {
			rowRange: "active"
		}, hozAlign: "center", headerSort: false
	},
	{
		title: __('Date'), field: 'date', formatter: function (cell, formatterParams, onRendered) {
			const cellValue = cell.getValue();

			if (!cellValue) {
				return null;
			}

			return frappe.datetime.str_to_user(cellValue)
		},
	},
	{ title: __('Party'), field: 'party', width: "20%" },
	{
		title: __('Amount'), field: 'amount', width: "20%", formatter: function (cell, formatterParams, onRendered) {
			const cellValue = cell.getValue();
			const row = cell.getRow();
			const cellRowData = row.getData();

			if (!cellValue) {
				return null;
			}

			return format_currency(cellValue, cellRowData.currency)
		},
	},
	{ title: __('Reference'), field: 'reference_string', width: "30%" },
	{ title: __('Reference Date'), field: 'reference_date' },
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

const matching_documents = {
	'Payment Entry': [],
	'Journal Entry': [],
	'Sales Invoice': [],
	'Purchase Invoice': []
}
// Todo: extend this with a hook
if (Object.keys(frappe.boot.module_app).filter(f => f == "hr").length) {
	Object.assign(matching_documents, {"Expense Claim": []})
}

const emit = defineEmits(['documentsChange'])
function onSelectedRowsChange () {
	var selectedData = tabulator.value.getSelectedData();
	emit('documentsChange', selectedData)
}

function change_doctype (dt) {
	document_type.value = dt;
	get_linked_docs(true);
}

function get_linked_docs (match) {
	frappe.xcall('erpnext.accounts.page.bank_reconciliation.bank_transaction_match.get_linked_payments',
		{
			bank_transactions: props.transactions,
			document_type: document_type.value,
			match: match
		}
	).then((result) => {
		const mapped_result = result.map(document => ({...document,
			date: document.posting_date,
			doctype: document_type.value,
			link: `/app/Form/${document_type.value}/${document.name}`
		}))

		Object.assign(matching_documents, {[document_type.value]: mapped_result});
		tableData.value = mapped_result
	})
}

function create_new_document() {
	if (document_type.value == "Payment Entry") {
		frappe.xcall('erpnext.accounts.doctype.bank_transaction.bank_transaction.make_new_document',{
			document_type: document_type.value,
			transactions: props.transactions
		}).then(r => {
			const doclist = frappe.model.sync(r);
			frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
		})
	} else {
		frappe.new_doc(document_type.value)
	}
}

onMounted(() => {
	tabulator.value = new Tabulator(matchingbox.value, {
		data: tableData.value,
		columns: columns,
		selectable: true,
		placeholder: function() {
			return !props.transactions.length ? __("Select a bank transaction to find matching transactions") : __("No matching document found for your selection")
		}
	});

	tabulator.value.on("rowSelectionChanged", function(data, rows, selected, deselected) {
		onSelectedRowsChange()
	});
})

watch(() => props.transactions, () => {
	get_linked_docs(true)
});

watch(tableData, (newData, oldData) => {
	tabulator.value.replaceData(newData);
})

</script>

<style lang='scss'>
.matching-box {
	.section-title {
		border-bottom: 1px solid #d1d8dd;
		margin-bottom: 10px;
		text-transform: uppercase;
	}

	table.vgt-table {
		font-size: 1rem;
	}
}

.document-options {
	margin: 20px;
}

.no-data {
	margin: 25px;
	height: 150px;
}

.documents-table {
	margin-top: 15px;
}
</style>
