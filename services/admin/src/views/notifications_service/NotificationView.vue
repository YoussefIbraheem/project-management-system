<script setup>
import { onMounted, ref, watch } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import Table from "../../components/Table.vue";

const router = useRouter();

const columns = [
    { key: "id", label: "ID", align: "left" },
    { key: "user_id", label: "User ID", align: "left" },
    { key: "type", label: "Type", align: "left" },
    { key: "subject", label: "Subject", align: "left" },
    { key: "body", label: "Body", align: "left" },
    { key: "is_read", label: "Is Read", align: "left" },
    { key: "created_at", label: "Created At", align: "left" },
];

const notifications = ref([]);
const loading = ref(false);
const error = ref("");

async function fetchNotifications() {
    loading.value = true;
    error.value = "";
    try {
        const response = await axios.get(
            "http://localhost:8081/api/v1/notifications/",
        );
        notifications.value = response.data;
    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
}

onMounted(fetchNotifications);
watch(() => router.currentRoute.value.path, fetchNotifications);
watch(() => router.currentRoute.value.query, fetchNotifications, { deep: true });
</script>

<template>
    <section class="notification-view">
        <h1>Notifications</h1>
        <Table
            :columns="columns"
            :rows="notifications"
            :loading="loading"
            :error="error"
            emptyText="No Notifications found"
        />
    </section>
</template>

<style scoped>
.notification-view h1 {
    margin-bottom: 1rem;
    color: var(--color-heading);
}
</style>
