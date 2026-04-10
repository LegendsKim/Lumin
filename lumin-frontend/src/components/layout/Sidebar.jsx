import React from 'react'
import { NavLink } from 'react-router-dom'
import { ROUTES } from '../../config/constants'

const Sidebar = () => {
  return (
    <aside className="sidebar" id="sidebar">
      <NavLink to={ROUTES.DASHBOARD} style={{ textDecoration: 'none' }}>
          <div className="sidebar-logo">
              <div className="logo-icon">💡</div>
              <div className="logo-text">Lumin</div>
              <div className="logo-tagline">האור של העסק שלך</div>
          </div>
      </NavLink>

      <nav className="sidebar-menu sidebar-nav">
          <div className="menu-section">
              <div className="menu-section-title">תפריט ראשי</div>
              <div className="menu-item">
                  <NavLink to={ROUTES.DASHBOARD} className={({ isActive }) => `menu-link nav-item ${isActive ? 'active' : ''}`}>
                      <span className="menu-icon nav-icon">📊</span>
                      <span>דשבורד</span>
                  </NavLink>
              </div>
              <div className="menu-item">
                  <NavLink to="/inventory" className={({ isActive }) => `menu-link nav-item ${isActive ? 'active' : ''}`}>
                      <span className="menu-icon nav-icon">📦</span>
                      <span>מוצרים</span>
                  </NavLink>
              </div>
              <div className="menu-item">
                  <NavLink to="/sales" className={({ isActive }) => `menu-link nav-item ${isActive ? 'active' : ''}`}>
                      <span className="menu-icon nav-icon">🛒</span>
                      <span>הזמנות</span>
                  </NavLink>
              </div>
              <div className="menu-item">
                  <NavLink to="/customers" className={({ isActive }) => `menu-link nav-item ${isActive ? 'active' : ''}`}>
                      <span className="menu-icon nav-icon">👥</span>
                      <span>לקוחות</span>
                  </NavLink>
              </div>
          </div>
          
          <div className="menu-section">
              <div className="menu-section-title">כלים</div>
              <div className="menu-item">
                  <NavLink to="/settings" className={({ isActive }) => `menu-link nav-item ${isActive ? 'active' : ''}`}>
                      <span className="menu-icon nav-icon">⚙️</span>
                      <span>הגדרות</span>
                  </NavLink>
              </div>
          </div>
      </nav>

      <div className="sidebar-user">
          <img className="user-avatar"
               src="https://ui-avatars.com/api/?name=Admin+User&background=00ADB5&color=fff&size=128"
               alt="User" />
          <div className="user-info">
              <div className="user-name">מנהל אזורי</div>
              <div className="user-role">מנהל</div>
          </div>
          <div className="user-logout" title="התנתק">🚪</div>
      </div>
    </aside>
  )
}

export default Sidebar
