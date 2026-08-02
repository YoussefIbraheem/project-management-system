<script setup>
import { onMounted, ref, watch } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import Table from "../../components/Table.vue";

const router = useRouter();

const columns = [
    { key: "id", label: "ID", align: "left" },
    { key: "actor_id", label: "Actor ID", align: "left" },
    { key: "subject_id", label: "Subject ID", align: "left" },
    { key: "subject_type", label: "Subject Type", align: "left" },
    { key: "service", label: "Service", align: "left" },
    { key: "action", label: "Action", align: "left" },
    { key: "metadata", label: "metadata", align: "left" },
];

const events = ref([]);
const loading = ref(false);
const error = ref("");

async function fetchEvents() {
    loading.value = true;
    error.value = "";
    try {
      const response = await axios.get("http://localhost:5006/api/v1/events/");
        console.log(response.data);
        events.value = response.data;
    } catch (err) {
        error.value =
            err.response?.data?.error?.message || "Failed to load events.";
    } finally {
        loading.value = false;
    }
}
onMounted(fetchEvents);
watch(() => router.currentRoute.value.path, fetchEvents);
watch(() => router.currentRoute.value.query, fetchEvents, { deep: true });
</script>

<template>
    <section class="event-view">
        <h1>Events</h1>
        <Table
            :columns="columns"
            :rows="events"
            :title="'Events'"
            :loading="loading"
            :error="error"
            emptyText="No Events found"
        />
    </section>
</template>

<style scoped>
.event-view h1 {
    margin-bottom: 1rem;
    color: var(--color-heading);
}
</style>
