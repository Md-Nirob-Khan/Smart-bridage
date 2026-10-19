import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const links = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/bridges', label: 'Bridges' },
  { to: '/inspections/new', label: 'New Inspection', write: true },
  { to: '/reports', label: 'Reports' },
]

export default function Layout() {
  const { user, logout, canWrite } = useAuth()
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()

  const item = ({ isActive }) =>
    `block rounded-md px-3 py-2 text-sm font-medium ${isActive ? 'bg-white/15 text-white' : 'text-blue-100 hover:bg-white/10'}`

  return (
    <div className="min-h-screen md:flex">
      {/* Mobile top bar */}
      <div className="flex items-center justify-between bg-brand-900 px-4 py-3 text-white md:hidden">
        <span className="font-semibold">SmartBridge AI</span>
        <button onClick={() => setOpen(!open)} className="text-2xl leading-none" aria-label="Menu">☰</button>
      </div>

      <aside className={`${open ? 'block' : 'hidden'} bg-brand-900 p-4 md:block md:w-60 md:shrink-0`}>
        <div className="mb-6 hidden text-lg font-bold text-white md:block">SmartBridge AI</div>
        <nav className="space-y-1" onClick={() => setOpen(false)}>
          {links.filter((l) => !l.write || canWrite).map((l) => (
            <NavLink key={l.to} to={l.to} end={l.end} className={item}>{l.label}</NavLink>
          ))}
        </nav>
        <div className="mt-6 border-t border-white/20 pt-4 text-sm text-blue-100">
          <div className="font-medium text-white">{user.name}</div>
          <div className="mb-3 capitalize">{user.role}</div>
          <button className="text-blue-200 underline" onClick={() => { logout(); navigate('/login') }}>Log out</button>
        </div>
      </aside>

      <main className="min-w-0 flex-1 p-4 sm:p-6"><Outlet /></main>
    </div>
  )
}
