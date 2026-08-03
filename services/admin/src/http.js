import axios from 'axios'
import { router } from './router'
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from './auth'

const REFRESH_URL = `${import.meta.env.VITE_AUTH_API_URL}/api/v1/login/refresh/`

axios.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let refreshPromise = null

function refreshAccessToken() {
  if (!refreshPromise) {
    const refresh = getRefreshToken()
    refreshPromise = axios
      .post(REFRESH_URL, { refresh })
      .then((response) => {
        setTokens({
          access: response.data.access,
          refresh: response.data.refresh,
        })
        return response.data.access
      })
      .finally(() => {
        refreshPromise = null
      })
  }
  return refreshPromise
}

axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error

    if (!response || config.url === REFRESH_URL) {
      return Promise.reject(error)
    }

    if (response.status === 401 && !config._retry && getRefreshToken()) {
      config._retry = true
      try {
        const access = await refreshAccessToken()
        config.headers.Authorization = `Bearer ${access}`
        return axios(config)
      } catch (refreshError) {
        clearTokens()
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }

    if (response.status === 401) {
      clearTokens()
      router.push('/login')
    }

    return Promise.reject(error)
  },
)
