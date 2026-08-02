import './assets/main.css'
import App from './App.vue'
import { router } from './router'
import { createApp } from 'vue'
import axios from 'axios'
import { getAccessToken } from './auth'

axios.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

createApp(App).use(router).mount("#app")
