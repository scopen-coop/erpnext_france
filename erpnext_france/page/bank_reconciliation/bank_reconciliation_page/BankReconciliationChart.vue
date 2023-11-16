<template>
	<div class="card my-3 chart-card">
		<frappe-charts
			v-if="showChart"
			ref="chart"
			:id="'reconciliation-chart'"
			:dataSets="data.datasets || []"
			:labels="data.labels"
			:title="title"
			:type="chartType"
			:colors="colors"
			:height="chartHeight"
			:axisOptions="axisOptions"
			:tooltipOptions="tooltipOptions"
			:lineOptions="lineOptions"
		/>
	</div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

import FrappeCharts from '../../../../../../frappe/frappe/public/js/lib/FrappeCharts.vue';

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
	}
})

const showChart = ref(false)
const data = ref([])
const title = ref(null)
const chartType = ref('line')
const colors = ref([])
const lineOptions = ref({})
const axisOptions = ref({})
const tooltipOptions = ref({})
const chartHeight = ref(null)


function getChartData() {
	if (props.bank_account && props.start_date && props.end_date) {
		frappe.xcall('erpnext.accounts.page.bank_reconciliation.bank_transaction_match.get_statement_chart',
			{
				account: props.bank_account,
				start_date: props.start_date,
				end_date: props.end_date
			}
		)
		.then(r => {
			if (r && !r.exc && Object.keys(r).length) {
				data.value = r.data
				title.value = r.title
				chartType.value = r.type
				colors.value = r.colors
				lineOptions.value = r.lineOptions
				showChart.value = true
			} else {
				showChart.value = false
			}
		})
	}
}

onMounted(() => {
	getChartData()
})

watch(() => [props.bank_account, props.start_date, props.end_date], () => {
	getChartData()
});

defineExpose({
	getChartData
})

</script>

<style lang='scss' scoped>
	.chart-card {
		border: none;
	}
</style>