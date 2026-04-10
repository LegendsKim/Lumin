import React from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

const MainLayout = () => {
    return (
        <div className="flex h-screen bg-neutral-50 overflow-hidden">
            {/* Sidebar (Fixed Right) */}
            <Sidebar />

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col md:mr-64 overflow-hidden transition-all duration-300">
                <Header />

                <main className="flex-1 overflow-y-auto p-6 md:p-8">
                    <div className="max-w-7xl mx-auto animate-fade-in">
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    )
}

export default MainLayout
