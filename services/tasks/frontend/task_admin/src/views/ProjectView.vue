<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import Table from '../components/Table.vue'

const columns = [
  { key: 'id', label: 'ID', align: 'left' },
  { key: 'name', label: 'Name', align: 'left' },
  { key: 'description', label: 'Description', align: 'left' },
  { key: 'created_at', label: 'Created At', align: 'left' },
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
    console.log(response)
  } catch (err) {
    error.value = `Failed to load projects.${err}`
  } finally {
    loading.value = false
  }
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
    />
  </section>
</template>

<style scoped>
.project-view h1 {
  margin-bottom: 1rem;
  color: var(--color-heading);
}
</style>
