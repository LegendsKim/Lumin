import React from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

const MainLayout = () => {
    return (
        <>
            <div className="sidebar-overlay" id="sidebarOverlay"></div>
            <Sidebar />
            
            <div className="main-content">
                <Header />
                <div className="content-area">
                    <Outlet />
                </div>
            </div>
        </>
    )
}

export default MainLayout
