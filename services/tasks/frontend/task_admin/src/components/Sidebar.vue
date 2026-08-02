<script setup>
defineProps({
  routes: {
    type: Array,
    required: true,
  },
})
</script>

<template>
  <aside class="sidebar">
    <nav class="sidebar__nav">
      <ul>
        <li v-for="route in routes" :key="route.path">
          <RouterLink :to="route.path" class="sidebar__link">
            {{ route.label }}
          </RouterLink>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 200px;
  flex-shrink: 0;
  background: var(--color-chrome-background);
  border-right: 1px solid var(--color-chrome-border);
  padding: 1.5rem 1rem;
}

.sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sidebar__nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.sidebar__link {
  display: block;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  color: var(--color-chrome-text);
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: 700;
}

.sidebar__link:hover {
  background: var(--color-chrome-background-hover);
}

.sidebar__link.router-link-active {
  background: var(--color-chrome-background-hover);
}
</style>
