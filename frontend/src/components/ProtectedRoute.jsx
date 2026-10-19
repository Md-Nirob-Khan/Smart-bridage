import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/** Requires login; pass `write` to also require admin/engineer. */
export default function ProtectedRoute({ write = false }) {
  const { user, loading, canWrite } = useAuth()
  if (loading) return <p className="p-6 text-slate-500">Loading…</p>
  if (!user) return <Navigate to="/login" replace />
  if (write && !canWrite) return <Navigate to="/" replace />
  return <Outlet />
}
