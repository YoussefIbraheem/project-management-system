<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import Table from '../components/Table.vue'

const router = useRouter()

const columns = [
  { key: 'id', label: 'ID', align: 'left' },
  { key: 'name', label: 'Name', align: 'left' },
  { key: 'description', label: 'Description', align: 'left' },
  { key: 'created_at', label: 'Created At', align: 'left' },
  { key: 'actions', label: 'Actions', align: 'left' },
]

const projects = ref([])
const loading = ref(false)
const error = ref('')

async function fetchProjects() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('http://localhost:8080/api/v1/projects/')
    projects.value = response.data
  } catch (err) {
    error.value = `Failed to load projects.${err}`
  } finally {
    loading.value = false
  }
}

function goToBoards(project) {
  router.push(`/projects/${project.id}/boards`)
}

function goToMembers(project) {
  router.push(`/projects/${project.id}/members`)
}

onMounted(fetchProjects)
</script>

<template>
  <section class="project-view">
    <h1>Projects</h1>
    <Table
      :columns="columns"
      :rows="projects"
      :loading="loading"
      :error="error"
      empty-text="No projects found."
      @row-click="goToBoards"
    >
      <template #cell(actions)="{ row }">
        <button
          type="button"
          class="project-view__action"
          @click.stop="goToBoards(row)"
        >
          Boards
        </button>
        <button
          type="button"
          class="project-view__action"
          @click.stop="goToMembers(row)"
        >
          Members
        </button>
      </template>
    </Table>
  </section>
</template>

<style scoped>
.project-view h1 {
  margin-bottom: 1rem;
  color: var(--color-heading);
}

.project-view__action {
  padding: 0.3rem 0.6rem;
  margin-right: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-background);
  color: var(--color-text);
  font-size: 0.8rem;
  cursor: pointer;
}

.project-view__action:hover {
  border-color: var(--color-border-hover);
}
</style>
