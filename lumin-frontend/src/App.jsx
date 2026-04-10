import { Routes, Route, Navigate } from 'react-router-dom'
import { ROUTES } from './config/constants'
import MainLayout from './components/layout/MainLayout'

// Placeholder components - will be created in later phases
const HomePage = () => <div className="p-8 text-center"><h1 className="text-4xl font-bold text-gradient-lumin">ברוכים הבאים ל-Lumin</h1><p className="mt-4 text-neutral-600">האור של העסק שלך</p></div>
const LoginPage = () => <div className="p-8"><h1 className="text-2xl font-bold">התחברות</h1></div>
const DashboardPage = () => <div className="p-8"><h1 className="text-2xl font-bold">לוח בקרה</h1></div>
const NotFoundPage = () => <div className="p-8 text-center"><h1 className="text-2xl font-bold">404 - הדף לא נמצא</h1></div>

function App() {
  return (
    <div className="min-h-screen bg-neutral-50">
      <Routes>
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />

        {/* Protected Routes */}
        <Route element={<MainLayout />}>
          <Route path={ROUTES.HOME} element={<DashboardPage />} /> {/* Treating Home as Dashboard for now */}
          <Route path={ROUTES.DASHBOARD} element={<DashboardPage />} />
          <Route path="/inventory" element={<div className="p-8"><h1>מלאי (Inventory)</h1></div>} />
          <Route path="/sales" element={<div className="p-8"><h1>מכירות (Sales)</h1></div>} />
          <Route path="/customers" element={<div className="p-8"><h1>לקוחות (Customers)</h1></div>} />
          <Route path="/settings" element={<div className="p-8"><h1>הגדרות (Settings)</h1></div>} />
        </Route>

        <Route path={ROUTES.NOT_FOUND} element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to={ROUTES.NOT_FOUND} replace />} />
      </Routes>
    </div>
  )
}

export default App
