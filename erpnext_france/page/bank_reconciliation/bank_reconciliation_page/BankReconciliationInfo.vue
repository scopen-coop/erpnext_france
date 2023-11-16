<template>
	<div class="flex flex-wrap justify-center align-center">
		<div class="balance-info-card">
			<div class="text-center border rounded w-shadow bg-white">
				<div class="balance-info">
					<p class="strong">{{ transaction_initial_balance }}</p>
					<p>{{ __("Initial balance") }}</p>
				</div>
			</div>
		</div>
		<div class="balance-info-card">
			<div class="text-center border rounded w-shadow bg-white">
				<div class="balance-info">
					<p class="strong">{{ transaction_final_balance }}</p>
					<p>{{ __("Final balance") }}</p>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	name: 'BankReconciliationInfo',
	props: {
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
		}
	},
	data() {
		return {
			transaction_initial_balance: 0,
			transaction_final_balance: 0
		}
	},
	mounted() {
		this.get_initial_balance()
		this.get_final_balance()
	},
	watch: {
		bank_account: function() {
			this.get_initial_balance()
			this.get_final_balance()
		},
		start_date: function() {
			this.get_initial_balance()
		},
		end_date: function() {
			this.get_final_balance()
		}
	},
	methods: {
		get_initial_balance: function() {
			if (this.bank_account && this.start_date) {
				frappe.xcall('erpnext.accounts.page.bank_reconciliation.bank_transaction_match.get_initial_balance',
					{
						account: this.bank_account,
						start_date: this.start_date
					}
				).then(r => {
					if (r) {
						this.transaction_initial_balance = r.formatted_balance;
					}
				})
			}
		},
		get_final_balance: function() {
			if (this.bank_account && this.end_date) {
				frappe.xcall('erpnext.accounts.page.bank_reconciliation.bank_transaction_match.get_final_balance',
					{
						account: this.bank_account,
						end_date: this.end_date
					}
				).then(r => {
					if (r) {
						this.transaction_final_balance = r.formatted_balance;
					}
				})
			}
		},

	}

}
</script>

<style lang='scss' scoped>
.balance-info-card {
	width: 25%;
	padding-right: 15px;
	padding-bottom: 15px;
	position: relative;
	margin: 5px;

	.balance-info {
		p {
			margin: 5px 0px;
		}
	}

	.w-shadow {
		box-shadow: 0 10px 15px -3px rgba(0,0,0,.1), 0 4px 6px -2px rgba(0,0,0,.05);
	}
}
</style>