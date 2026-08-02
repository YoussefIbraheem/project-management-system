<script setup>
import { onMounted, ref, watch } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'
import Table from '../../components/Table.vue'

const props = defineProps({
  projectId: {
    type: String,
    required: true,
  },
})

const route = useRoute()
const router = useRouter()

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
      params: { project_id: props.projectId, board_id: route.query.boardId },
    })
    tasks.value = response.data
  } catch (err) {
    error.value = err.response?.data?.error?.message || 'Failed to load tasks.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchTasks)
watch(() => [props.projectId, route.query.boardId], fetchTasks)
</script>

<template>
  <section class="task-view">
    <button type="button" class="task-view__back" @click="router.push('/projects')">
      &larr; Back to Projects
    </button>
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
  padding: 0.4rem 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-background);
  color: var(--color-text);
  font-size: 0.85rem;
  cursor: pointer;
}

.task-view__back:hover {
  border-color: var(--color-border-hover);
}
</style>
