<script setup>
defineProps({
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
})

defineEmits(['row-click'])
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
          v-for="row in rows"
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
</style>
