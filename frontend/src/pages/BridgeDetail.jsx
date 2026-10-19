import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import api, { errorMessage } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function BridgeDetail() {
  const { id } = useParams()
  const { canWrite, isAdmin } = useAuth()
  const navigate = useNavigate()
  const [b, setB] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get(`/bridges/${id}`).then((r) => setB(r.data)).catch((e) => setError(errorMessage(e)))
  }, [id])

  const remove = async () => {
    if (!window.confirm(`Delete ${b.name}? This also deletes all its inspections.`)) return
    try { await api.delete(`/bridges/${id}`); navigate('/bridges') } catch (e) { setError(errorMessage(e)) }
  }

  if (error) return <div className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</div>
  if (!b) return <p className="text-slate-500">Loading…</p>

  const rows = [
    ['Code', b.code], ['Location', b.location], ['Type', b.bridge_type],
    ['Length', b.length_m != null && `${b.length_m} m`], ['Construction year', b.construction_year],
    ['Daily traffic', b.daily_traffic?.toLocaleString()], ['Last inspection', b.last_inspection_date],
    ['Coordinates', b.latitude != null && b.longitude != null && `${b.latitude}, ${b.longitude}`],
  ]

  return (
    <div className="space-y-4">
      <Link to="/bridges" className="text-sm text-brand-600 hover:underline">← All bridges</Link>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-xl font-semibold">{b.name}</h1>
        <div className="flex gap-2">
          {canWrite && <Link to={`/bridges/${id}/edit`} className="btn-secondary">Edit</Link>}
          {isAdmin && <button onClick={remove} className="btn-danger">Delete</button>}
        </div>
      </div>
      <div className="card">
        <dl className="grid gap-x-6 gap-y-3 sm:grid-cols-2">
          {rows.map(([k, v]) => (
            <div key={k}><dt className="text-xs uppercase text-slate-500">{k}</dt><dd>{v || '—'}</dd></div>
          ))}
        </dl>
        {b.notes && <p className="mt-4 whitespace-pre-wrap border-t pt-4 text-sm">{b.notes}</p>}
      </div>
      <div className="card text-sm text-slate-500">Inspection history and risk trend appear here in Phases 5–7.</div>
    </div>
  )
}
