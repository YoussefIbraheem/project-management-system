<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { clearTokens } from '../auth'
import { navItems } from '../router.js'

const router = useRouter()
const openDropdown = ref(null)

function toggleDropdown(label) {
  openDropdown.value = openDropdown.value === label ? null : label
}

function closeDropdowns() {
  openDropdown.value = null
}

function logout() {
  clearTokens()
  router.push('/login')
}
</script>

<template>
  <header class="navbar" @click="closeDropdowns">
    <span class="navbar__brand">Task Admin</span>
    <nav class="navbar__links">
      <template v-for="item in navItems" :key="item.label">
        <RouterLink
          v-if="!item.children"
          :to="item.path"
          class="navbar__link"
          active-class="navbar__link--active"
        >
          {{ item.label }}
        </RouterLink>
        <div v-else class="navbar__dropdown" @click.stop>
          <button
            type="button"
            class="navbar__link navbar__dropdown-trigger"
            @click="toggleDropdown(item.label)"
          >
            {{ item.label }}
          </button>
          <div v-if="openDropdown === item.label" class="navbar__dropdown-menu">
            <RouterLink
              v-for="child in item.children"
              :key="child.path"
              :to="child.path"
              class="navbar__dropdown-item"
              active-class="navbar__link--active"
              @click="closeDropdowns"
            >
              {{ child.label }}
            </RouterLink>
          </div>
        </div>
      </template>
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

.navbar__links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.navbar__link {
  padding: 0.4rem 0.75rem;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--color-chrome-text);
  font-size: 0.85rem;
  text-decoration: none;
  cursor: pointer;
}

.navbar__link:hover {
  background: var(--color-chrome-background-hover);
}

.navbar__link--active {
  font-weight: 600;
  background: var(--color-chrome-background-hover);
}

.navbar__dropdown {
  position: relative;
}

.navbar__dropdown-trigger {
  font: inherit;
}

.navbar__dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 0.25rem;
  min-width: 100%;
  border: 1px solid var(--color-chrome-border);
  border-radius: 6px;
  background: var(--color-chrome-background);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 10;
}

.navbar__dropdown-item {
  display: block;
  padding: 0.4rem 0.75rem;
  color: var(--color-chrome-text);
  font-size: 0.85rem;
  text-decoration: none;
  white-space: nowrap;
}

.navbar__dropdown-item:hover {
  background: var(--color-chrome-background-hover);
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
