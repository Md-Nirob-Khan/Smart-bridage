import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Bridges from './pages/Bridges'
import BridgeDetail from './pages/BridgeDetail'
import BridgeEdit from './pages/BridgeEdit'
import ComingSoon from './pages/ComingSoon'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/bridges" element={<Bridges />} />
          <Route path="/bridges/:id" element={<BridgeDetail />} />
          <Route path="/reports" element={<ComingSoon title="Reports" phase={7} />} />
          <Route element={<ProtectedRoute write />}>
            <Route path="/bridges/new" element={<BridgeEdit />} />
            <Route path="/bridges/:id/edit" element={<BridgeEdit />} />
            <Route path="/inspections/new" element={<ComingSoon title="New Inspection" phase={4} />} />
          </Route>
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
