import { Routes, Route, Navigate } from 'react-router-dom'
import { ROUTES } from './config/constants'

// Placeholder components - will be created in later phases
const HomePage = () => <div className="p-8 text-center"><h1 className="text-4xl font-bold text-gradient-lumin">ברוכים הבאים ל-Lumin</h1><p className="mt-4 text-neutral-600">האור של העסק שלך</p></div>
const LoginPage = () => <div className="p-8"><h1 className="text-2xl font-bold">התחברות</h1></div>
const DashboardPage = () => <div className="p-8"><h1 className="text-2xl font-bold">לוח בקרה</h1></div>
const NotFoundPage = () => <div className="p-8 text-center"><h1 className="text-2xl font-bold">404 - הדף לא נמצא</h1></div>

function App() {
  return (
    <div className="min-h-screen bg-neutral-50">
      <Routes>
        <Route path={ROUTES.HOME} element={<HomePage />} />
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
        <Route path={ROUTES.DASHBOARD} element={<DashboardPage />} />
        <Route path={ROUTES.NOT_FOUND} element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to={ROUTES.NOT_FOUND} replace />} />
      </Routes>
    </div>
  )
}

export default App
