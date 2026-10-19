import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import api, { errorMessage } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Bridges() {
  const { canWrite } = useAuth()
  const [bridges, setBridges] = useState(null)
  const [error, setError] = useState('')
  const [q, setQ] = useState('')

  useEffect(() => {
    api.get('/bridges').then((r) => setBridges(r.data)).catch((e) => setError(errorMessage(e)))
  }, [])

  const shown = useMemo(() => {
    const s = q.trim().toLowerCase()
    return (bridges || []).filter((b) => !s || [b.code, b.name, b.location, b.bridge_type].some((v) => v?.toLowerCase().includes(s)))
  }, [bridges, q])

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-xl font-semibold">Bridges</h1>
        {canWrite && <Link to="/bridges/new" className="btn-primary">+ Add bridge</Link>}
      </div>
      <input className="input max-w-sm" placeholder="Search code, name, location, type…" value={q} onChange={(e) => setQ(e.target.value)} />
      {error && <div className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      {!bridges && !error && <p className="text-slate-500">Loading…</p>}
      {bridges && (
        <div className="card overflow-x-auto p-0 sm:p-0">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3">Code</th><th className="px-4 py-3">Name</th>
                <th className="hidden px-4 py-3 sm:table-cell">Location</th>
                <th className="hidden px-4 py-3 md:table-cell">Type</th>
                <th className="hidden px-4 py-3 md:table-cell">Built</th>
                <th className="hidden px-4 py-3 lg:table-cell">Traffic/day</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((b) => (
                <tr key={b.id} className="border-t hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono">{b.code}</td>
                  <td className="px-4 py-3"><Link className="font-medium text-brand-600 hover:underline" to={`/bridges/${b.id}`}>{b.name}</Link></td>
                  <td className="hidden px-4 py-3 sm:table-cell">{b.location || '—'}</td>
                  <td className="hidden px-4 py-3 md:table-cell">{b.bridge_type || '—'}</td>
                  <td className="hidden px-4 py-3 md:table-cell">{b.construction_year || '—'}</td>
                  <td className="hidden px-4 py-3 lg:table-cell">{b.daily_traffic?.toLocaleString() ?? '—'}</td>
                </tr>
              ))}
              {shown.length === 0 && <tr><td colSpan={6} className="px-4 py-6 text-center text-slate-500">No bridges found.</td></tr>}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
