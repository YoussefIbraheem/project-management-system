<script setup>
import { onMounted, ref, watch } from 'vue'
import axios from 'axios'
import Table from '../components/Table.vue'

const props = defineProps({
  projectId: {
    type: String,
    required: true,
  },
  boardId: {
    type: String,
    required: true,
  },
})

const columns = [
  { key: 'id', label: 'ID', align: 'left' },
  { key: 'title', label: 'Title', align: 'left' },
  { key: 'priority', label: 'Priority', align: 'left' },
  { key: 'assignees', label: 'Assignees', align: 'left' },
  { key: 'due_date', label: 'Due Date', align: 'left' },
]

const tasks = ref([])
const loading = ref(false)
const error = ref('')

async function fetchTasks() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('http://localhost:8080/api/v1/tasks/', {
      params: { project_id: props.projectId, board_id: props.boardId },
    })
    tasks.value = response.data
  } catch (err) {
    error.value = err.response?.data?.error?.message || 'Failed to load tasks.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchTasks)
watch(() => [props.projectId, props.boardId], fetchTasks)
</script>

<template>
  <section class="task-view">
    <RouterLink :to="`/projects/${projectId}/boards`" class="task-view__back">
      &larr; Back to Boards
    </RouterLink>
    <h1>Tasks</h1>
    <Table
      :columns="columns"
      :rows="tasks"
      :loading="loading"
      :error="error"
      empty-text="No tasks found."
    >
      <template #cell(assignees)="{ value }">
        {{ value?.length ? value.map((assignee) => assignee.user_id).join(', ') : '—' }}
      </template>
    </Table>
  </section>
</template>

<style scoped>
.task-view h1 {
  margin-bottom: 1rem;
  color: var(--color-heading);
}

.task-view__back {
  display: inline-block;
  margin-bottom: 1rem;
  color: var(--color-text);
  font-size: 0.85rem;
}
</style>
