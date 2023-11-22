<template>
	<div v-show="bank_account && start_date && end_date">
		<BankReconciliationChart
			ref="reconciliationChart"
			:bank_account="bank_account"
			:start_date="start_date"
			:end_date="end_date"
		/>
		<BankReconciliationInfo
			:bank_account="bank_account"
			:start_date="start_date"
			:end_date="end_date"
		/>
		<BankReconciliationActions
			:selected_transactions="selectedTransactions"
			:selected_documents="selectedDocuments"
			@resetList="reset_list"
		/>
		<div class="row reconciliation-dashboard">
			<div class="col-md-6">
				<BankReconciliationTransactionList
					ref="transactionsList"
					:bank_account="bank_account"
					:start_date="start_date"
					:end_date="end_date"
					:selected_transactions="selectedTransactions"
					@transactionsChange="transactions_change"
				/>
			</div>
			 <div class="col-md-6">
				<BankReconciliationMatchingBox
					:transactions="selectedTransactions"
					@documentsChange="documents_change"
				/>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed} from 'vue'

import BankReconciliationChart from './BankReconciliationChart.vue';
import BankReconciliationTransactionList from './BankReconciliationTransactionList.vue';
import BankReconciliationInfo from './BankReconciliationInfo.vue';
import BankReconciliationMatchingBox from './BankReconciliationMatchingBox.vue';
import BankReconciliationActions from './BankReconciliationActions.vue';

const props = defineProps({
	bank_account: {
		type: String,
		default: null
	},
	date_range: {
		type: Array,
		default: () => []
	}
})

const bank_account = ref(props.bank_account)
const date_range = ref(props.date_range)
const transactionsList = ref(null)
const reconciliationChart = ref(null)
const selectedTransactions = ref([])
const selectedDocuments = ref([])

const start_date = computed(() => {
	return date_range.value[0]
})

const end_date = computed(() => {
	return date_range.value[1]
})

erpnext.bank_reconciliation.on('filter_change', data => {
	switch (data.name) {
		case 'BANK_ACCOUNT':
			bank_account.value = data.value;
			break;
		case 'DATE_RANGE':
			date_range.value = data.value;
			break;
	}
})

erpnext.bank_reconciliation.on('refresh', () => {
	reset_list()
})

function transactions_change(selection) {
	selectedTransactions.value = selection;
	check_selected_rows()
}

function documents_change(selection) {
	selectedDocuments.value = selection;
	check_selected_rows()
}

function check_selected_rows() {
	if (selectedTransactions.length > 1 && selectedDocuments.length > 1) {
		frappe.msgprint(__("Please select only one bank transaction and multiple documents or multiple bank transactions and only one document."))
	}
}

function reset_list() {
	transactionsList.value.get_transaction_list();
	reconciliationChart.value.getChartData();
}
</script>

<style lang='scss' scoped>
.reconciliation-dashboard {
	margin-top: 30px;
}

.reconciliation-btn {
	margin: 20px 0;
}
</style>
