<script setup>
import { onMounted, ref, watch } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import Table from "../../components/Table.vue";

const router = useRouter();

const columns = [
    { key: "id", label: "ID", align: "left" },
    { key: "email_address", label: "Email Address", align: "left" },
    { key: "notification_id", label: "Notification ID", align: "left" },
    { key: "recipient_email", label: "Recepient Email", align: "left" },
    { key: "status", label: "Status", align: "left" },
    { key: "attempts", label: "Attemps", align: "left" },
    { key: "error_message", label: "Error Message", align: "left" },
    { key: "sent_at", label: "Sent At", align: "left" },
    { key: "created_at", label: "Created At", align: "left" },
];

const emails_logs = ref([]);
const loading = ref(false);
const error = ref("");

async function fetchEmailsLogs() {
    loading.value = true;
    error.value = "";
    try {
        const response = await axios.get(
            `${import.meta.env.VITE_NOTIFICATIONS_API_URL}/api/v1/email-logs/`,
        );
        emails_logs.value = response.data;
    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
}

onMounted(fetchEmailsLogs);
watch(() => router.currentRoute.value.path, fetchEmailsLogs);
watch(() => router.currentRoute.value.query, fetchEmailsLogs, { deep: true });
</script>

<template>
    <section class="email-log-view">
        <h1>Email Logs</h1>
        <Table
            :columns="columns"
            :rows="emails_logs"
            :loading="loading"
            :error="error"
            emptyText="No Email Logs found"
        />
    </section>
</template>

<style scoped>
.email-log-view h1 {
    margin-bottom: 1rem;
    color: var(--color-heading);
}
</style>
