<script setup>
import { useRouter } from 'vue-router'
import { clearTokens } from '../auth'

const router = useRouter()

function logout() {
  clearTokens()
  router.push('/login')
}
</script>

<template>
  <header class="navbar">
    <span class="navbar__brand">Task Admin</span>
    <nav class="navbar__links">
      <button type="button" class="navbar__logout" @click="logout">Logout</button>
    </nav>
  </header>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  border-bottom: 1px solid var(--color-chrome-border);
  background: var(--color-chrome-background);
}

.navbar__brand {
  font-weight: 600;
  color: var(--color-chrome-text);
}

.navbar__logout {
  padding: 0.4rem 0.9rem;
  border: 1px solid var(--color-chrome-border);
  border-radius: 6px;
  background: transparent;
  color: var(--color-chrome-text);
  font-size: 0.85rem;
  cursor: pointer;
}

.navbar__logout:hover {
  background: var(--color-chrome-background-hover);
}
</style>
