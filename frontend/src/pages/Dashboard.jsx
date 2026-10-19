import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const { user } = useAuth()
  return (
    <div className="card">
      <h1 className="text-xl font-semibold">Welcome, {user.name}</h1>
      <p className="mt-2 text-slate-500">Dashboard charts and priority table arrive in Phase 6.</p>
    </div>
  )
}
