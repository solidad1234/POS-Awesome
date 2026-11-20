<template>
	<div>
		<!-- Date Range Filter -->
		<v-row class="dashboard-grid mb-2">
			<v-col cols="12">
				<DateRangeFilter
					:from-date="fromDate"
					:to-date="toDate"
					:today-label="__('Today')"
					:seven-days-label="__('7 days')"
					:thirty-days-label="__('30 days')"
					:start-label="__('From Date')"
					:end-label="__('To Date')"
					:aria-label="__('Margin report date range')"
					color="primary"
					@update:from-date="$emit('update:fromDate', $event)"
					@update:to-date="$emit('update:toDate', $event)"
				/>
			</v-col>
		</v-row>

		<!-- Summary Cards -->
		<v-row class="dashboard-grid mb-2">
			<v-col cols="12">
				<v-card class="dashboard-card" elevation="2">
					<div class="dashboard-card__header">
						<h2 class="text-subtitle-1 font-weight-bold mb-0">
							{{ __("Sales Margin Report") }}
						</h2>
						<div class="dashboard-chip-row">
							<v-chip size="small" color="info" variant="tonal">
								{{ rangeLabel }}
							</v-chip>
							<v-chip size="small" color="success" variant="tonal">
								{{ __("Items") }}: {{ summary.item_count ?? 0 }}
							</v-chip>
							<v-chip
								size="small"
								:color="avgMarginColor"
								variant="tonal"
							>
								{{ __("Avg Margin") }}:
								{{ formatPercent(summary.avg_margin_pct, 1) }}
							</v-chip>
						</div>
					</div>

					<div class="summary-grid">
						<SummaryMetric
							:label="__('Total Revenue')"
							:value="formatMoney(Number(summary.total_ext_price || 0))"
						/>
						<SummaryMetric
							:label="__('Total Cost')"
							:value="formatMoney(Number(summary.total_ext_cost || 0))"
						/>
						<SummaryMetric
							:label="__('Total Margin')"
							:value="formatMoney(Number(summary.total_margin || 0))"
							:value-class="
								Number(summary.total_margin || 0) < 0
									? 'summary-metric__value--danger'
									: ''
							"
						/>
						<SummaryMetric
							:label="__('Avg Margin %')"
							:value="formatPercent(summary.avg_margin_pct, 1)"
						/>
					</div>
				</v-card>
			</v-col>
		</v-row>

		<!-- Data Table -->
		<v-row class="dashboard-grid mb-2">
			<v-col cols="12">
				<v-card class="dashboard-card" elevation="2">
					<div class="dashboard-card__header">
						<h2 class="text-subtitle-1 font-weight-bold mb-0">
							{{ __("Item-wise Margin Breakdown") }}
						</h2>
					</div>

					<!-- Search box -->
					<div class="margin-report-search px-4 pb-3">
						<v-text-field
							v-model="searchText"
							:placeholder="__('Search by item name or department\u2026')"
							prepend-inner-icon="mdi-magnify"
							variant="outlined"
							density="compact"
							hide-details
							clearable
							class="margin-search-field"
						/>
					</div>

					<v-data-table
						v-if="rows.length"
						:headers="tableHeaders"
						:items="filteredRows"
						:items-per-page="itemsPerPage"
						density="compact"
						class="margin-report-table"
						:no-data-text="__('No results match your search.')"
					>
						<!-- Department -->
						<template #item.department="{ item }">
							<span class="text-caption font-weight-medium">
								{{ item.department || __("Uncategorized") }}
							</span>
						</template>

						<!-- Item Name -->
						<template #item.item_name="{ item }">
							<div>
								<div class="font-weight-medium">{{ item.item_name || item.item_code }}</div>
								<div class="text-caption text-disabled">{{ item.item_code }}</div>
							</div>
						</template>

						<!-- Qty Sold -->
						<template #item.qty_sold="{ item }">
							<span class="font-weight-medium">
								{{ formatQuantity(Number(item.qty_sold || 0)) }}
							</span>
						</template>

						<!-- Ext Price -->
						<template #item.ext_price="{ item }">
							<span>{{ formatMoney(Number(item.ext_price || 0)) }}</span>
						</template>

						<!-- Ext Cost -->
						<template #item.ext_cost="{ item }">
							<span>{{ formatMoney(Number(item.ext_cost || 0)) }}</span>
						</template>

						<!-- Total Margin -->
						<template #item.total_margin="{ item }">
							<span
								class="font-weight-bold"
								:class="Number(item.total_margin || 0) < 0 ? 'text-error' : 'text-success'"
							>
								{{ formatMoney(Number(item.total_margin || 0)) }}
							</span>
						</template>

						<!-- Margin % with color chip -->
						<template #item.margin_pct="{ item }">
							<v-chip
								:color="marginChipColor(item.margin_pct)"
								size="x-small"
								variant="tonal"
								class="font-weight-bold"
							>
								{{ item.margin_pct != null ? formatPercent(item.margin_pct, 2) : "\u2014" }}
							</v-chip>
						</template>

						<template #bottom>
							<div class="margin-report-footer px-4 py-2 d-flex flex-wrap align-center ga-4">
								<span class="text-caption text-disabled">
									{{ filteredRows.length }} {{ __("items") }}
									<template v-if="searchText">
										({{ __("filtered from") }} {{ rows.length }})
									</template>
								</span>
								<v-spacer />
								<v-select
									v-model="itemsPerPage"
									:items="pageSizeItems"
									density="compact"
									variant="outlined"
									hide-details
									style="max-width: 110px"
									:label="__('Per page')"
								/>
							</div>
						</template>
					</v-data-table>

					<EmptyState
						v-else
						:message="__('No sales margin data found for this period.')"
					/>
				</v-card>
			</v-col>
		</v-row>
	</div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { MarginReportRow } from "@/posapp/services/dashboardService";
import EmptyState from "./EmptyState.vue";
import SummaryMetric from "./SummaryMetric.vue";
import DateRangeFilter from "@/posapp/components/pos/shared/DateRangeFilter.vue";

const __ = (value: string) => ((window as any).__ ? (window as any).__(value) : value);

const props = defineProps<{
	rows: MarginReportRow[];
	summary: {
		total_ext_price: number;
		total_ext_cost: number;
		total_margin: number;
		avg_margin_pct?: number | null;
		item_count: number;
	};
	rangeLabel: string;
	formatMoney: (v: number) => string;
	formatQuantity: (v: number) => string;
	formatPercent: (v: number | null | undefined, decimals?: number) => string;
	fromDate?: string;
	toDate?: string;
	loading?: boolean;
}>();

const emit = defineEmits<{
	(e: "update:fromDate", value: string): void;
	(e: "update:toDate", value: string): void;
}>();

const searchText = ref("");
const itemsPerPage = ref(25);
const pageSizeItems = [10, 25, 50, 100, -1];

const tableHeaders = computed(() => [
	{
		title: __("Department"),
		key: "department",
		sortable: true,
	},
	{
		title: __("Item Name"),
		key: "item_name",
		sortable: true,
	},
	{
		title: __("Qty Sold"),
		key: "qty_sold",
		sortable: true,
		align: "end" as const,
	},
	{
		title: __("Ext Price"),
		key: "ext_price",
		sortable: true,
		align: "end" as const,
	},
	{
		title: __("Ext Cost"),
		key: "ext_cost",
		sortable: true,
		align: "end" as const,
	},
	{
		title: __("Total Margin \$"),
		key: "total_margin",
		sortable: true,
		align: "end" as const,
	},
	{
		title: __("Margin %"),
		key: "margin_pct",
		sortable: true,
		align: "end" as const,
	},
]);

const filteredRows = computed(() => {
	if (!searchText.value) return props.rows;
	const q = searchText.value.toLowerCase();
	return props.rows.filter(
		(r) =>
			(r.item_name || "").toLowerCase().includes(q) ||
			(r.item_code || "").toLowerCase().includes(q) ||
			(r.department || "").toLowerCase().includes(q),
	);
});

function marginChipColor(pct: number | null | undefined): string {
	if (pct == null) return "default";
	if (pct < 0) return "error";
	if (pct < 10) return "warning";
	if (pct < 30) return "info";
	return "success";
}

const avgMarginColor = computed(() => marginChipColor(props.summary.avg_margin_pct));
</script>

<style scoped>
.margin-search-field {
	max-width: 420px;
}

.margin-report-table :deep(th) {
	font-weight: 600 !important;
	font-size: 0.75rem !important;
	text-transform: uppercase;
	letter-spacing: 0.04em;
	white-space: nowrap;
}

.margin-report-table :deep(td) {
	font-size: 0.8125rem !important;
}

.margin-report-footer {
	border-top: 1px solid rgba(0, 0, 0, 0.08);
}
</style>
