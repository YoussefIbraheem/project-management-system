import { createMemoryHistory, createRouter } from 'vue-router'
import ProjectView from './views/ProjectView.vue'
import LoginView from './views/LoginView.vue'
import { isAuthenticated } from './auth'

export const routes = [
  { path: '/projects', component: ProjectView, label: 'Projects' },
]

export const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    ...routes,
    { path: '/login', component: LoginView },
    { path: '/', redirect: '/projects' },
  ],
})

router.beforeEach((to) => {
  if (to.path !== '/login' && !isAuthenticated()) {
    return '/login'
  }
  if (to.path === '/login' && isAuthenticated()) {
    return '/projects'
  }
})
