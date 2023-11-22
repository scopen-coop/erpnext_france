<template>
	<div class="flex flex-wrap justify-center">
		<div class="actions-wrapper border rounded">
			<div class="flex flex-wrap justify-center align-center">
				<div class="amount-recap">
					<h4>{{ __("Bank Transactions") }}</h4>
					<p class="strong">{{ transactions_formatted_amount }}</p>
				</div>
				<div class="amount-recap">
					<h4>{{ __("Documents") }}</h4>
					<p class="strong">{{ documents_formatted_amount }}</p>
				</div>
			</div>
			<div class="flex flex-wrap justify-center align-center">
				<a type="button"
					:class='(is_reconciliation_disabled || btn_clicked) ? "btn btn-success disabled" : "btn btn-success"'
					:disabled="is_reconciliation_disabled || btn_clicked" @click="reconcile_entries"><span>{{ btn_clicked ?
						__("In progress...") : __("Reconcile", null, "Bank Transaction") }}</span><i v-show="!btn_clicked"
						class='uil uil-check'></i></a>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['resetList'])

const props = defineProps({
	selected_transactions: {
		type: Array,
		default: () => []
	},
	selected_documents: {
		type: Array,
		default: () => []
	}
})

const btn_clicked = ref(false);

function get_transactions_amount() {
	return Math.abs(props.selected_transactions.reduce((p, v) => {
		return p + v.amount;
	}, 0))
}

function get_documents_amount() {
	return Math.abs(props.selected_documents.reduce((p, v) => {
		return p + v.amount;
	}, 0))
}

function get_currency() {
	return props.selected_transactions[0]?.currency;
}

const is_reconciliation_disabled = computed(() => {
	return get_transactions_amount() == 0 || get_documents_amount() == 0;
})

const is_pos = computed(() => {
	return props.selected_documents.filter(f => (f.is_pos == 1 || f.is_paid == 1));
})

const transactions_formatted_amount = computed(() => {
	return format_currency(get_transactions_amount(), get_currency())
})

const documents_formatted_amount = computed(() => {
	return format_currency(get_documents_amount(), get_currency())
})

function reconcile_entries() {
	btn_clicked.value = true;
	if ((props.selected_transactions.length == 1 && props.selected_documents.length >= 1)
		|| (props.selected_transactions.length >= 1 && props.selected_documents.length == 1)) {
		if (["Sales Invoice", "Purchase Invoice", "Expense Claim"].includes(props.selected_documents[0]["doctype"]) && !is_pos.length) {
			frappe.confirm(__("This action will create a new payment entry. Do you confirm ?"), () => {
				call_reconciliation()
			});
		} else {
			call_reconciliation()
		}
	} else {
		frappe.msgprint(__("You can only reconcile one bank transaction with several documents or several bank transactions with one document."))
		btn_clicked.value = false;
	}
}

function call_reconciliation() {
	frappe.xcall('erpnext.accounts.page.bank_reconciliation.bank_reconciliation.reconcile',
		{
			bank_transactions: props.selected_transactions,
			documents: !is_pos.length ? props.selected_documents : is_pos
		}
	).then(() => {
		emit('resetList')
		btn_clicked.value = false;
		const message = __("{0} documents reconciled", [props.selected_documents.length]);
		frappe.show_alert({ message, indicator: "green" })
	}).catch(r => {
		btn_clicked.value = false;
	})
}

</script>


<style lang='scss' scoped>
.amount-recap {
	margin: 20px;
	text-align: center;
	padding: 0 20px 0 20px;
}

.actions-wrapper {
	padding: 15px;
	width: 50%;
}

.btn-success,
.btn-success:hover {
	color: #fff;
}</style>