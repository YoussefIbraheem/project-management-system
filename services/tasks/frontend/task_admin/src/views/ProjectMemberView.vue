<script setup>
import { onMounted, ref, watch } from 'vue'
import axios from 'axios'
import Table from '../components/Table.vue'

const props = defineProps({
  projectId: {
    type: String,
    required: true,
  },
})

const columns = [
  { key: 'user_id', label: 'User ID', align: 'left' },
  { key: 'role', label: 'Role', align: 'left' },
]

const members = ref([])
const loading = ref(false)
const error = ref('')

async function fetchMembers() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get(
      `http://localhost:8080/api/v1/projects/${props.projectId}/members`,
    )
    members.value = response.data
  } catch (err) {
    error.value = err.response?.data?.error?.message || 'Failed to load members.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchMembers)
watch(() => props.projectId, fetchMembers)
</script>

<template>
  <section class="member-view">
    <RouterLink to="/projects" class="member-view__back">&larr; Back to Projects</RouterLink>
    <h1>Project Members</h1>
    <Table
      :columns="columns"
      :rows="members"
      row-key="user_id"
      :loading="loading"
      :error="error"
      empty-text="No members found."
    />
  </section>
</template>

<style scoped>
.member-view h1 {
  margin-bottom: 1rem;
  color: var(--color-heading);
}

.member-view__back {
  display: inline-block;
  margin-bottom: 1rem;
  color: var(--color-text);
  font-size: 0.85rem;
}
</style>
