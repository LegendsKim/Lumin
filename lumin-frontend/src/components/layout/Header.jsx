import React from 'react'

const Header = () => {
    return (
        <header className="top-bar">
            <div className="top-bar-left">
                <h1>שלום לך! 👋</h1>
                <p>סיכום הביצועים שלך להיום</p>
            </div>
            <div className="top-bar-right">
                <button className="hamburger-menu" id="hamburgerBtn" aria-label="תפריט">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
                <div className="top-bar-icon">🔍</div>
                <div className="top-bar-icon has-notification">🔔</div>
                <div className="top-bar-icon has-notification">✉️</div>
            </div>
        </header>
    )
}

export default Header
