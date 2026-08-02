<script setup>
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'
import Sidebar from './components/Sidebar.vue'
import { routes } from './router'

const route = useRoute()
</script>

<template>
  <template v-if="route.path === '/login'">
    <RouterView />
  </template>
  <template v-else>
    <Navbar />
    <div class="layout">
      <Sidebar :routes="routes" />
      <main class="content">
        <RouterView />
      </main>
    </div>
  </template>
</template>

<style scoped>
.layout {
  display: flex;
  flex: 1;
}

.content {
  flex: 1;
  padding: 1.5rem;
}
</style>
