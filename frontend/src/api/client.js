import axios from 'axios'

const TOKEN_KEY = 'sb_token'
export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t) => (t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY))

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((cfg) => {
  const t = getToken()
  if (t) cfg.headers.Authorization = `Bearer ${t}`
  return cfg
})

// Expired/invalid token: drop it and send the user to login.
api.interceptors.response.use(
  (r) => r,
  (err) => {
    const isLogin = err.config?.url?.includes('/auth/login')
    if (err.response?.status === 401 && !isLogin) {
      setToken(null)
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

/** Turn a FastAPI error into a readable string. */
export function errorMessage(err) {
  const d = err.response?.data?.detail
  if (Array.isArray(d)) return d.map((e) => `${e.loc.slice(1).join('.')}: ${e.msg}`).join('; ')
  return d || err.message || 'Something went wrong'
}

export default api
