import { createMemoryHistory, createRouter } from 'vue-router'
import ProjectView from './views/ProjectView.vue'
import BoardView from './views/BoardView.vue'
import TaskView from './views/TaskView.vue'
import ProjectMemberView from './views/ProjectMemberView.vue'
import LoginView from './views/LoginView.vue'
import { isAuthenticated } from './auth'

export const routes = [{ path: '/projects', component: ProjectView }]

const detailRoutes = [
  { path: '/projects/:projectId/boards', component: BoardView, props: true },
  {
    path: '/projects/:projectId/tasks',
    component: TaskView,
    props: true,
  },
  { path: '/projects/:projectId/members', component: ProjectMemberView, props: true },
]

export const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    ...routes,
    ...detailRoutes,
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
