import { useState } from 'react'
import { errorMessage } from '../api/client'

export const BRIDGE_TYPES = ['RCC', 'Steel', 'Prestressed', 'Composite', 'Masonry', 'Other']

const EMPTY = {
  code: '', name: '', location: '', latitude: '', longitude: '', length_m: '',
  construction_year: '', bridge_type: '', daily_traffic: '', last_inspection_date: '', notes: '',
}
const NUMERIC = ['latitude', 'longitude', 'length_m', 'construction_year', 'daily_traffic']

/** Convert form strings to API payload: '' -> null, numeric fields -> numbers. */
function toPayload(f) {
  const out = {}
  for (const [k, v] of Object.entries(f)) {
    out[k] = v === '' || v == null ? null : NUMERIC.includes(k) ? Number(v) : v
  }
  return out
}

export default function BridgeForm({ initial, onSubmit, submitLabel, onCancel }) {
  const [f, setF] = useState({ ...EMPTY, ...Object.fromEntries(Object.entries(initial || {}).map(([k, v]) => [k, v ?? ''])) })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setError(''); setSaving(true)
    try { await onSubmit(toPayload(f)) } catch (err) { setError(errorMessage(err)); setSaving(false) }
  }

  // Plain function (not a component) so inputs keep focus between keystrokes.
  const field = (k, label, type = 'text', rest = {}) => (
    <div>
      <label className="label" htmlFor={k}>{label}</label>
      <input id={k} key={k} className="input" type={type} value={f[k]} onChange={set(k)} {...rest} />
    </div>
  )

  return (
    <form onSubmit={submit} className="card space-y-4">
      {error && <div className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      <div className="grid gap-4 sm:grid-cols-2">
        {field('code', 'Bridge code *', 'text', { required: true })}
        {field('name', 'Name *', 'text', { required: true })}
        {field('location', 'Location', 'text', {})}
        <div>
          <label className="label" htmlFor="bridge_type">Bridge type</label>
          <select id="bridge_type" className="input" value={f.bridge_type} onChange={set('bridge_type')}>
            <option value="">—</option>
            {BRIDGE_TYPES.map((t) => <option key={t}>{t}</option>)}
          </select>
        </div>
        {field('latitude', 'Latitude', 'number', { step: 'any', min: '-90', max: '90' })}
        {field('longitude', 'Longitude', 'number', { step: 'any', min: '-180', max: '180' })}
        {field('length_m', 'Length (m)', 'number', { step: 'any', min: '0' })}
        {field('construction_year', 'Construction year', 'number', { min: '1800', max: '2100' })}
        {field('daily_traffic', 'Daily traffic (vehicles)', 'number', { min: '0' })}
        {field('last_inspection_date', 'Last inspection date', 'date', {})}
      </div>
      <div>
        <label className="label" htmlFor="notes">Notes</label>
        <textarea id="notes" rows={3} className="input" value={f.notes} onChange={set('notes')} />
      </div>
      <div className="flex gap-2">
        <button className="btn-primary" disabled={saving}>{saving ? 'Saving…' : submitLabel}</button>
        <button type="button" className="btn-secondary" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  )
}
