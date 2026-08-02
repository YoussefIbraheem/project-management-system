<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  columns: {
    // [{ key: 'title', label: 'Title', align: 'left' }]
    type: Array,
    required: true,
  },
  rows: {
    type: Array,
    default: () => [],
  },
  rowKey: {
    type: String,
    default: 'id',
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: '',
  },
  emptyText: {
    type: String,
    default: 'No records found.',
  },
  pageSize: {
    type: Number,
    default: 10,
  },
})

defineEmits(['row-click'])

const currentPage = ref(1)

const totalPages = computed(() =>
  Math.max(1, Math.ceil(props.rows.length / props.pageSize)),
)

const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * props.pageSize
  return props.rows.slice(start, start + props.pageSize)
})

const rangeStart = computed(() =>
  props.rows.length === 0 ? 0 : (currentPage.value - 1) * props.pageSize + 1,
)

const rangeEnd = computed(() =>
  Math.min(currentPage.value * props.pageSize, props.rows.length),
)

watch(
  () => props.rows,
  () => {
    currentPage.value = 1
  },
)

watch(totalPages, (pages) => {
  if (currentPage.value > pages) {
    currentPage.value = pages
  }
})

function goToPage(page) {
  currentPage.value = Math.min(Math.max(1, page), totalPages.value)
}
</script>

<template>
  <div class="table-wrapper">
    <table class="data-table">
      <thead>
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            :style="{ textAlign: column.align || 'left' }"
          >
            <slot :name="`header(${column.key})`" :column="column">
              {{ column.label }}
            </slot>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td :colspan="columns.length" class="state-cell">
            <slot name="loading">Loading...</slot>
          </td>
        </tr>
        <tr v-else-if="error">
          <td :colspan="columns.length" class="state-cell state-cell--error">
            <slot name="error" :error="error">{{ error }}</slot>
          </td>
        </tr>
        <tr v-else-if="!rows.length">
          <td :colspan="columns.length" class="state-cell">
            <slot name="empty">{{ emptyText }}</slot>
          </td>
        </tr>
        <tr
          v-else
          v-for="row in pagedRows"
          :key="row[rowKey]"
          class="data-row"
          @click="$emit('row-click', row)"
        >
          <td
            v-for="column in columns"
            :key="column.key"
            :style="{ textAlign: column.align || 'left' }"
          >
            <slot :name="`cell(${column.key})`" :row="row" :value="row[column.key]" :column="column">
              {{ row[column.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="!loading && !error && rows.length" class="table-pagination">
      <span class="table-pagination__summary">
        Showing {{ rangeStart }}–{{ rangeEnd }} of {{ rows.length }}
      </span>
      <div class="table-pagination__controls">
        <button
          type="button"
          class="table-pagination__button"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          Prev
        </button>
        <span class="table-pagination__page">Page {{ currentPage }} of {{ totalPages }}</span>
        <button
          type="button"
          class="table-pagination__button"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.table-wrapper {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: 8px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.data-table thead {
  background: var(--color-background-soft);
}

.data-table th {
  padding: 0.75rem 1rem;
  font-weight: 600;
  color: var(--color-heading);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.data-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.data-row:hover {
  background-color: var(--color-background-mute);
}

.state-cell {
  padding: 1.5rem 1rem;
  text-align: center;
  color: var(--color-text);
  opacity: 0.7;
}

.state-cell--error {
  color: #e04444;
  opacity: 1;
}

.table-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
  font-size: 0.85rem;
  color: var(--color-text);
}

.table-pagination__controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.table-pagination__button {
  padding: 0.35rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-background);
  color: var(--color-text);
  font-size: 0.85rem;
  cursor: pointer;
}

.table-pagination__button:hover:not(:disabled) {
  border-color: var(--color-border-hover);
}

.table-pagination__button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
