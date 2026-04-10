import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ROUTES } from '../config/constants';
import '../styles/home.css';

const Home = () => {
    useEffect(() => {
        const handleScroll = () => {
            const navbar = document.getElementById('navbar');
            if (navbar) {
                if (window.scrollY > 50) {
                    navbar.classList.add('scrolled');
                } else {
                    navbar.classList.remove('scrolled');
                }
            }
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const scrollToSection = (e, id) => {
        e.preventDefault();
        const target = document.querySelector(id);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    };

    return (
        <div className="home-wrapper" dir="rtl">
            {/* Navigation */}
            <nav id="navbar">
                <div className="logo">Lumin</div>
                <div className="nav-links">
                    <a href="#features" onClick={(e) => scrollToSection(e, '#features')}>תכונות</a>
                    <a href="#pricing" onClick={(e) => scrollToSection(e, '#pricing')}>מחירים</a>
                    <a href="#testimonials" onClick={(e) => scrollToSection(e, '#testimonials')}>עדויות</a>
                    <Link to={ROUTES.LOGIN} className="btn-login">כניסה למערכת</Link>
                </div>
                <Link className="mobile-menu-btn" to={ROUTES.LOGIN} style={{textDecoration: 'none'}}>☰</Link>
            </nav>

            {/* Hero Section */}
            <section className="hero">
                <div className="hero-container">
                    <div className="hero-content fade-in-up">
                        <h1>
                            נהל את העסק שלך<br />
                            <span className="highlight">בצורה החכמה ביותר</span>
                        </h1>
                        <p>
                            מערכת ניהול עסקית מתקדמת לניהול לקוחות, טיפולים, מלאי ומכירות.
                            הכל במקום אחד, פשוט ויעיל. התחל להגדיל את הרווחיות שלך עוד היום!
                        </p>
                        <div className="hero-buttons">
                            <Link to={ROUTES.LOGIN} className="btn-primary">
                                התחל חינם
                                <span>←</span>
                            </Link>
                            <a href="#pricing" onClick={(e) => scrollToSection(e, '#pricing')} className="btn-secondary">
                                ראה מחירים
                                <span>↓</span>
                            </a>
                        </div>
                        <p className="hero-trust">✓ ללא צורך בכרטיס אשראי · ✓ ביטול בכל עת · ✓ תמיכה 24/7</p>
                    </div>

                    <div className="hero-visual">
                        <div className="dashboard-preview">
                            <div className="status-badge">המערכת פעילה</div>
                            <div className="preview-header">
                                <div className="preview-avatar">L</div>
                                <div className="preview-info">
                                    <h3>Lumin Dashboard</h3>
                                    <p>ניהול עסק חכם ומתקדם</p>
                                </div>
                            </div>
                            <div className="preview-stats">
                                <div className="preview-stat">
                                    <div className="preview-stat-value">₪120K</div>
                                    <div className="preview-stat-label">הכנסות החודש</div>
                                </div>
                                <div className="preview-stat">
                                    <div className="preview-stat-value">450</div>
                                    <div className="preview-stat-label">לקוחות פעילים</div>
                                </div>
                                <div className="preview-stat">
                                    <div className="preview-stat-value">98%</div>
                                    <div className="preview-stat-label">שביעות רצון</div>
                                </div>
                                <div className="preview-stat">
                                    <div className="preview-stat-value">1,200</div>
                                    <div className="preview-stat-label">טיפולים בחודש</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="stats-section">
                <div className="stats-grid">
                    <div className="stat-item">
                        <h3>10,000+</h3>
                        <p>עסקים משתמשים</p>
                    </div>
                    <div className="stat-item">
                        <h3>99.9%</h3>
                        <p>זמינות שירות</p>
                    </div>
                    <div className="stat-item">
                        <h3>24/7</h3>
                        <p>תמיכה טכנית</p>
                    </div>
                    <div className="stat-item">
                        <h3>₪2M+</h3>
                        <p>הכנסות נוספות ללקוחותינו</p>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="features-section" id="features">
                <div className="section-header">
                    <h2>כל מה שאתה צריך במקום אחד</h2>
                    <p>מערכת מקיפה לניהול כל היבטי העסק שלך - מלקוחות ועד מכירות</p>
                </div>
                <div className="features-grid">
                    <div className="feature-card">
                        <div className="feature-icon">👥</div>
                        <h3 className="feature-title">ניהול לקוחות מתקדם</h3>
                        <p className="feature-desc">
                            מעקב מלא אחר כל לקוח - פרטים אישיים, היסטוריית טיפולים,
                            העדפות ותשלומים. CRM מובנה עם תזכורות אוטומטיות.
                        </p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">💆</div>
                        <h3 className="feature-title">ניהול טיפולים</h3>
                        <p className="feature-desc">
                            תיעוד מפורט של כל טיפול - מטפל, סוג טיפול, מחיר והערות.
                            דוחות ואנליטיקה על ביצועים ורווחיות.
                        </p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">📦</div>
                        <h3 className="feature-title">ניהול מלאי</h3>
                        <p className="feature-desc">
                            מעקב אחר מוצרים, כמויות ומחירים. התראות על מלאי נמוך
                            וסנכרון אוטומטי עם WooCommerce.
                        </p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">💰</div>
                        <h3 className="feature-title">מערכת תשלומים</h3>
                        <p className="feature-desc">
                            ניהול חשבוניות, תשלומים וחובות. חיבור לכל אמצעי התשלום
                            הפופולריים בישראל.
                        </p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">📊</div>
                        <h3 className="feature-title">דוחות ואנליטיקה</h3>
                        <p className="feature-desc">
                            דוחות מפורטים על מכירות, הכנסות, לקוחות ומגמות.
                            קבל תובנות עסקיות לקבלת החלטות נכונות.
                        </p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">🔄</div>
                        <h3 className="feature-title">סנכרון עם WooCommerce</h3>
                        <p className="feature-desc">
                            חיבור ישיר לחנות ה-WooCommerce שלך. סנכרון אוטומטי של
                            מוצרים, הזמנות ולקוחות.
                        </p>
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section className="pricing-section" id="pricing">
                <div className="section-header">
                    <h2>מחירים שמתאימים לכל עסק</h2>
                    <p>בחר את התוכנית המתאימה לך - כולן עם גישה מלאה לכל התכונות</p>
                </div>
                <div className="pricing-grid">
                    <div className="pricing-card">
                        <div className="pricing-header">
                            <h3>Basic</h3>
                            <p>מושלם לעסקים קטנים</p>
                        </div>
                        <div className="pricing-price">
                            <div className="price-amount">
                                <span className="price-currency">₪</span>
                                99
                                <span className="price-period">/חודש</span>
                            </div>
                        </div>
                        <ul className="pricing-features">
                            <li>עד 100 לקוחות</li>
                            <li>ניהול טיפולים בסיסי</li>
                            <li>דוחות חודשיים</li>
                            <li>תמיכה באימייל</li>
                            <li>גיבוי שבועי</li>
                        </ul>
                        <Link to={ROUTES.LOGIN}><button className="pricing-btn">התחל עכשיו</button></Link>
                    </div>

                    <div className="pricing-card featured">
                        <div className="popular-badge">הכי פופולרי ⭐</div>
                        <div className="pricing-header">
                            <h3>Professional</h3>
                            <p>לעסקים מתפתחים</p>
                        </div>
                        <div className="pricing-price">
                            <div className="price-amount">
                                <span className="price-currency">₪</span>
                                249
                                <span className="price-period">/חודש</span>
                            </div>
                        </div>
                        <ul className="pricing-features">
                            <li>לקוחות ללא הגבלה</li>
                            <li>כל תכונות הניהול</li>
                            <li>דוחות מתקדמים</li>
                            <li>תמיכה 24/7</li>
                            <li>גיבוי יומי</li>
                            <li>סנכרון WooCommerce</li>
                            <li>API מלא</li>
                        </ul>
                        <Link to={ROUTES.LOGIN}><button className="pricing-btn">התחל עכשיו</button></Link>
                    </div>

                    <div className="pricing-card">
                        <div className="pricing-header">
                            <h3>Enterprise</h3>
                            <p>לעסקים גדולים</p>
                        </div>
                        <div className="pricing-price">
                            <div className="price-amount">
                                <span className="price-currency">₪</span>
                                499
                                <span className="price-period">/חודש</span>
                            </div>
                        </div>
                        <ul className="pricing-features">
                            <li>כל תכונות Professional</li>
                            <li>מספר סניפים</li>
                            <li>ניהול צוות מתקדם</li>
                            <li>מנהל חשבון ייעודי</li>
                            <li>התאמות אישיות</li>
                            <li>אינטגרציות מיוחדות</li>
                            <li>SLA מובטח</li>
                        </ul>
                        <Link to={ROUTES.LOGIN}><button className="pricing-btn">צור קשר</button></Link>
                    </div>
                </div>
            </section>

            {/* Testimonials Section */}
            <section className="testimonials-section" id="testimonials">
                <div className="section-header">
                    <h2>מה הלקוחות שלנו אומרים</h2>
                    <p>אלפי עסקים כבר משתמשים ב-Lumin ומצליחים יותר</p>
                </div>
                <div className="testimonials-grid">
                    <div className="testimonial-card">
                        <p className="testimonial-text">
                            "Lumin שינה לנו את החיים! הניהול הפך להיות הרבה יותר פשוט
                            והרווחים עלו ב-40%. ממליצה בחום!"
                        </p>
                        <div className="testimonial-author">
                            <div className="author-avatar">ש</div>
                            <div className="author-info">
                                <h4>שרה כהן</h4>
                                <p>בעלת סלון יופי, תל אביב</p>
                            </div>
                        </div>
                    </div>

                    <div className="testimonial-card">
                        <p className="testimonial-text">
                            "המערכת הכי טובה שניסיתי. פשוטה לשימוש, עם כל מה שצריך.
                            התמיכה מצוינת והמחיר הוגן!"
                        </p>
                        <div className="testimonial-author">
                            <div className="author-avatar">ד</div>
                            <div className="author-info">
                                <h4>דוד לוי</h4>
                                <p>בעל קליניקה לטיפולים, ירושלים</p>
                            </div>
                        </div>
                    </div>

                    <div className="testimonial-card">
                        <p className="testimonial-text">
                            "עברנו ל-Lumin לפני שנה ולא מסתכלים אחורה. חסכנו המון זמן
                            וכסף, והלקוחות מרוצים יותר!"
                        </p>
                        <div className="testimonial-author">
                            <div className="author-avatar">מ</div>
                            <div className="author-info">
                                <h4>מיכל אברהם</h4>
                                <p>בעלת רשת ספאים, חיפה</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta-section">
                <div className="cta-content">
                    <h2>מוכנים לקחת את העסק לשלב הבא?</h2>
                    <p>הצטרף לאלפי עסקים מצליחים שכבר משתמשים ב-Lumin</p>
                    <Link to={ROUTES.LOGIN} className="btn-primary">
                        התחל חינם עכשיו
                        <span>←</span>
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer>
                <div className="footer-content">
                    <div className="footer-brand">
                        <h3>Lumin ✨</h3>
                        <p>
                            מערכת ניהול עסקית מתקדמת שעוזרת לעסקים קטנים ובינוניים
                            לגדול ולהצליח. פשוט, יעיל ומקצועי.
                        </p>
                    </div>
                    <div className="footer-section">
                        <h4>מוצר</h4>
                        <ul>
                            <li><a href="#features" onClick={(e) => scrollToSection(e, '#features')}>תכונות</a></li>
                            <li><a href="#pricing" onClick={(e) => scrollToSection(e, '#pricing')}>מחירים</a></li>
                            <li><a href="#testimonials" onClick={(e) => scrollToSection(e, '#testimonials')}>עדויות</a></li>
                            <li><Link to={ROUTES.DASHBOARD}>דמו</Link></li>
                        </ul>
                    </div>
                    <div className="footer-section">
                        <h4>חברה</h4>
                        <ul>
                            <li><a href="#about">אודות</a></li>
                            <li><a href="#contact">צור קשר</a></li>
                            <li><a href="#careers">קריירה</a></li>
                            <li><a href="#blog">בלוג</a></li>
                        </ul>
                    </div>
                    <div className="footer-section">
                        <h4>משפטי</h4>
                        <ul>
                            <li><a href="#privacy">מדיניות פרטיות</a></li>
                            <li><a href="#terms">תנאי שימוש</a></li>
                            <li><a href="#security">אבטחה</a></li>
                        </ul>
                    </div>
                </div>
                <div className="footer-bottom">
                    <p>&copy; 2025 Lumin. כל הזכויות שמורות.</p>
                </div>
            </footer>
        </div>
    );
};

export default Home;
