import React from 'react'
import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Package, 
  ShoppingCart, 
  Users, 
  Settings, 
  LogOut 
} from 'lucide-react'
import { ROUTES } from '../../config/constants'

const Sidebar = () => {
  const navItems = [
    { icon: LayoutDashboard, label: 'לוח בקרה', to: ROUTES.DASHBOARD },
    { icon: Package, label: 'מלאי', to: '/inventory' },
    { icon: ShoppingCart, label: 'מכירות', to: '/sales' },
    { icon: Users, label: 'לקוחות', to: '/customers' },
    { icon: Settings, label: 'הגדרות', to: '/settings' },
  ]

  return (
    <aside className="fixed inset-y-0 right-0 z-50 w-64 bg-white border-l border-neutral-200 shadow-sm transition-transform duration-300 ease-in-out hidden md:flex flex-col">
      {/* Logo Area */}
      <div className="flex items-center justify-center h-16 border-b border-neutral-100">
        <h1 className="text-2xl font-bold bg-gradient-lumin bg-clip-text text-transparent">
          Lumin
        </h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 group ${
                isActive
                  ? 'bg-primary-50 text-primary-700 shadow-sm'
                  : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900'
              }`
            }
          >
            <item.icon className="w-5 h-5 ml-3" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer / User Profile */}
      <div className="p-4 border-t border-neutral-100">
        <button className="flex items-center w-full px-4 py-2 text-sm font-medium text-red-600 rounded-xl hover:bg-red-50 transition-colors">
          <LogOut className="w-5 h-5 ml-3" />
          התנתק
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
