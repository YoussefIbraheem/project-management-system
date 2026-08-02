<script setup>
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'

const route = useRoute()
</script>

<template>
  <template v-if="route.path === '/login'">
    <RouterView />
  </template>
  <template v-else>
    <Navbar />
    <main class="content">
      <RouterView />
    </main>
  </template>
</template>

<style scoped>
.content {
  flex: 1;
  padding: 1.5rem;
}
</style>
