<script setup>
import { onMounted, ref, watch } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import Table from "../../components/Table.vue";

const router = useRouter();

const columns = [
    { key: "user_id", label: "User ID", align: "left" },
    { key: "email", label: "Email", align: "left" },
    { key: "username", label: "Username", align: "left" },
    { key: "display_name", label: "Display Name", align: "left" },
];

const users_replicas = ref([]);
const loading = ref(false);
const error = ref("");

async function fetchUserReplicas() {
    loading.value = true;
    error.value = "";
    try {
        const response = await axios.get(
            `${import.meta.env.VITE_NOTIFICATIONS_API_URL}/api/v1/users_replicas/`,
        );
        users_replicas.value = response.data;
    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
}

onMounted(fetchUserReplicas);
watch(() => router.currentRoute.value.path, fetchUserReplicas);
watch(() => router.currentRoute.value.query, fetchUserReplicas, { deep: true });
</script>

<template>
    <section class="user-replica-view">
        <h1>Users Replicas</h1>
        <Table
            :columns="columns"
            :rows="users_replicas"
            :loading="loading"
            :error="error"
            emptyText="No Users found"
        />
    </section>
</template>

<style scoped>
.user-replica-view h1 {
    margin-bottom: 1rem;
    color: var(--color-heading);
}
</style>
