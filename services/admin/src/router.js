import { createMemoryHistory, createRouter } from "vue-router";
import ProjectView from "./views/tasks_service/ProjectView.vue";
import BoardView from "./views/tasks_service/BoardView.vue";
import TaskView from "./views/tasks_service/TaskView.vue";
import ProjectMemberView from "./views/tasks_service/ProjectMemberView.vue";
import LoginView from "./views/LoginView.vue";
import { isAuthenticated } from "./auth.js";
import EventView from "./views/events_service/EventView.vue";

export const routes = [
  { path: "/projects", component: ProjectView },
  { path: "/events", component: EventView },
];

// Drives Navbar.vue. Entries with a single `path` render as a plain link;
// entries with `children` render as a dropdown (for a future service that
// exposes multiple interchangeable top-level views).
export const navItems = [
  { label: "Projects", path: "/projects" },
  { label: "Events", path: "/events" },
];

const detailRoutes = [
  { path: "/projects/:projectId/boards", component: BoardView, props: true },
  {
    path: "/projects/:projectId/tasks",
    component: TaskView,
    props: true,
  },
  {
    path: "/projects/:projectId/members",
    component: ProjectMemberView,
    props: true,
  },
];

export const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    ...routes,
    ...detailRoutes,
    { path: "/login", component: LoginView },
    { path: "/", redirect: "/projects" },
  ],
});

router.beforeEach((to) => {
  if (to.path !== "/login" && !isAuthenticated()) {
    return "/login";
  }
  if (to.path === "/login" && isAuthenticated()) {
    return "/projects";
  }
});
