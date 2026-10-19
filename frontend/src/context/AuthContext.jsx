import { createContext, useContext, useEffect, useState } from 'react'
import api, { getToken, setToken } from '../api/client'

const AuthContext = createContext(null)
export const useAuth = () => useContext(AuthContext)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(!!getToken())

  useEffect(() => {
    if (!getToken()) return
    api.get('/auth/me').then((r) => setUser(r.data)).catch(() => setToken(null)).finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const form = new URLSearchParams({ username: email, password })
    const { data } = await api.post('/auth/login', form)
    setToken(data.access_token)
    setUser(data.user)
  }
  const logout = () => { setToken(null); setUser(null) }

  // Role helpers mirror the backend rules.
  const canWrite = user && ['admin', 'engineer'].includes(user.role)
  const isAdmin = user?.role === 'admin'

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, canWrite, isAdmin }}>
      {children}
    </AuthContext.Provider>
  )
}
