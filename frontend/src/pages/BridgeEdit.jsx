import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import api, { errorMessage } from '../api/client'
import BridgeForm from '../components/BridgeForm'

/** Handles both /bridges/new and /bridges/:id/edit. */
export default function BridgeEdit() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [initial, setInitial] = useState(id ? null : {})
  const [error, setError] = useState('')

  useEffect(() => {
    if (id) api.get(`/bridges/${id}`).then((r) => setInitial(r.data)).catch((e) => setError(errorMessage(e)))
  }, [id])

  const save = async (payload) => {
    const { data } = id ? await api.put(`/bridges/${id}`, payload) : await api.post('/bridges', payload)
    navigate(`/bridges/${data.id}`)
  }

  if (error) return <div className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</div>
  if (!initial) return <p className="text-slate-500">Loading…</p>

  return (
    <div className="max-w-3xl space-y-4">
      <h1 className="text-xl font-semibold">{id ? 'Edit bridge' : 'Add bridge'}</h1>
      <BridgeForm initial={initial} onSubmit={save} submitLabel={id ? 'Save changes' : 'Create bridge'} onCancel={() => navigate(-1)} />
    </div>
  )
}
