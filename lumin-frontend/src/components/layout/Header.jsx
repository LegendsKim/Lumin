import React from 'react'
import { Bell, Search } from 'lucide-react'

const Header = () => {
    return (
        <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-neutral-200">
            <div className="flex items-center justify-between h-16 px-6">
                {/* Right side (Breadcrumbs or Page Title - Placeholder) */}
                <div>
                    <h2 className="text-lg font-semibold text-neutral-800">דף ראשי</h2>
                </div>

                {/* Left side (Actions) */}
                <div className="flex items-center space-x-4 space-x-reverse">
                    {/* Search Bar */}
                    <div className="relative hidden md:block">
                        <input
                            type="text"
                            placeholder="חיפוש..."
                            className="w-64 pl-4 pr-10 py-1.5 text-sm bg-neutral-100 border-none rounded-full focus:ring-2 focus:ring-primary-500 transition-all"
                        />
                        <Search className="absolute right-3 top-1.5 w-4 h-4 text-neutral-400" />
                    </div>

                    {/* Notifications */}
                    <button className="relative p-2 text-neutral-500 hover:bg-neutral-100 rounded-full transition-colors">
                        <Bell className="w-5 h-5" />
                        <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
                    </button>

                    {/* Mobile Menu Button (Hamburger) - To be implemented */}
                </div>
            </div>
        </header>
    )
}

export default Header
