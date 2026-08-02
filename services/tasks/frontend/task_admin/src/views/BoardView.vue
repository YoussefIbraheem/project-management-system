<script setup>
import { onMounted, ref, watch } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import Table from '../components/Table.vue'

const props = defineProps({
  projectId: {
    type: String,
    required: true,
  },
})

const router = useRouter()

const columns = [
  { key: 'id', label: 'ID', align: 'left' },
  { key: 'name', label: 'Name', align: 'left' },
  { key: 'description', label: 'Description', align: 'left' },
  { key: 'columns', label: 'Columns', align: 'left' },
  { key: 'created_at', label: 'Created At', align: 'left' },
]

const boards = ref([])
const loading = ref(false)
const error = ref('')

async function fetchBoards() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('http://localhost:8080/api/v1/boards/', {
      params: { project_id: props.projectId },
    })
    boards.value = response.data
  } catch (err) {
    error.value = err.response?.data?.error?.message || 'Failed to load boards.'
  } finally {
    loading.value = false
  }
}

function goToTasks(board) {
  router.push(`/projects/${props.projectId}/boards/${board.id}/tasks`)
}

onMounted(fetchBoards)
watch(() => props.projectId, fetchBoards)
</script>

<template>
  <section class="board-view">
    <RouterLink to="/projects" class="board-view__back">&larr; Back to Projects</RouterLink>
    <h1>Boards</h1>
    <Table
      :columns="columns"
      :rows="boards"
      :loading="loading"
      :error="error"
      empty-text="No boards found."
      @row-click="goToTasks"
    >
      <template #cell(columns)="{ value }">
        {{ value?.length || 0 }}
      </template>
    </Table>
  </section>
</template>

<style scoped>
.board-view h1 {
  margin-bottom: 1rem;
  color: var(--color-heading);
}

.board-view__back {
  display: inline-block;
  margin-bottom: 1rem;
  color: var(--color-text);
  font-size: 0.85rem;
}
</style>
