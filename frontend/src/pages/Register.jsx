import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api, { errorMessage } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [f, setF] = useState({ name: '', email: '', password: '', role: 'engineer' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setError(''); setBusy(true)
    try {
      await api.post('/auth/register', f)
      await login(f.email, f.password)
      navigate('/')
    } catch (err) { setError(errorMessage(err)); setBusy(false) }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-brand-900 p-4">
      <form onSubmit={submit} className="card w-full max-w-sm space-y-4">
        <h1 className="text-xl font-bold text-brand-900">Create account</h1>
        {error && <div className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</div>}
        <div><label className="label" htmlFor="name">Name</label>
          <input id="name" className="input" required value={f.name} onChange={set('name')} /></div>
        <div><label className="label" htmlFor="email">Email</label>
          <input id="email" type="email" className="input" required value={f.email} onChange={set('email')} /></div>
        <div><label className="label" htmlFor="password">Password (min 6 characters)</label>
          <input id="password" type="password" minLength={6} maxLength={72} className="input" required value={f.password} onChange={set('password')} /></div>
        <div><label className="label" htmlFor="role">Role</label>
          <select id="role" className="input" value={f.role} onChange={set('role')}>
            <option value="engineer">Engineer / Inspector</option>
            <option value="viewer">Viewer</option>
          </select></div>
        <button className="btn-primary w-full" disabled={busy}>{busy ? 'Creating…' : 'Register'}</button>
        <p className="text-center text-sm">Have an account? <Link className="text-brand-600 underline" to="/login">Sign in</Link></p>
      </form>
    </div>
  )
}
