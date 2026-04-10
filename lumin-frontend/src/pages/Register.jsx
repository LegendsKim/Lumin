import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { supabase } from '../config/supabase';
import { ROUTES } from '../config/constants';
import '../styles/login.css'; // Reusing the exact same UI as login

const Register = () => {
    const navigate = useNavigate();
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleEmailSignUp = async (e) => {
        e.preventDefault();
        
        if (password !== confirmPassword) {
            return setError('הסיסמאות אינן תואמות');
        }

        setLoading(true);
        setError(null);
        
        try {
            const { error: signUpError } = await supabase.auth.signUp({
                email,
                password,
                options: {
                    data: {
                        full_name: fullName,
                    }
                }
            });
            
            if (signUpError) throw signUpError;
            
            // Supabase handles the session creation if email confirmation is off, 
            // otherwise you can instruct them to verify their email
            navigate(ROUTES.DASHBOARD);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleLogin = async (e) => {
        e.preventDefault();
        setError(null);
        
        try {
            const { error } = await supabase.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: `${window.location.origin}${ROUTES.DASHBOARD}`
                }
            });
            if (error) throw error;
        } catch (error) {
            setError(error.message);
        }
    };

    return (
        <div className="login-page-wrapper" dir="rtl">
            <div className="login-container">
                {/* Logo */}
                <div className="logo-section" style={{ marginBottom: '25px' }}>
                    <div className="logo-icon" style={{ fontSize: '48px', marginBottom: '10px' }}>💡</div>
                    <div className="logo-text" style={{ fontSize: '36px' }}>Lumin</div>
                    <div className="logo-tagline">הצטרף עכשיו והאר את העסק שלך</div>
                </div>

                {/* Welcome Text */}
                <div className="welcome-text" style={{ marginBottom: '24px' }}>
                    <h1 style={{ fontSize: '24px' }}>יצירת חשבון חדש 🚀</h1>
                    <p>מלא את הפרטים כדי להתחיל בחינם</p>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="error-message">
                        {error}
                    </div>
                )}

                {/* Registration Form */}
                <form className="login-form" onSubmit={handleEmailSignUp} style={{ gap: '16px' }}>
                    <div className="form-group">
                        <label htmlFor="fullName">שם מלא</label>
                        <input 
                            type="text" 
                            id="fullName" 
                            placeholder="ישראל ישראלי" 
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            required 
                        />
                    </div>
                    
                    <div className="form-group">
                        <label htmlFor="email">אימייל</label>
                        <input 
                            type="email" 
                            id="email" 
                            placeholder="example@email.com" 
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required 
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">סיסמה</label>
                        <input 
                            type="password" 
                            id="password" 
                            placeholder="••••••••" 
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required 
                            minLength="6"
                        />
                    </div>
                    
                    <div className="form-group">
                        <label htmlFor="confirmPassword">אישור סיסמה</label>
                        <input 
                            type="password" 
                            id="confirmPassword" 
                            placeholder="••••••••" 
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required 
                        />
                    </div>

                    <button type="submit" className="login-btn" disabled={loading} style={{ marginTop: '16px' }}>
                        {loading ? 'יוצר חשבון...' : 'פתח חשבון חינם!'}
                    </button>
                </form>

                {/* Divider */}
                <div className="divider" style={{ margin: '20px 0' }}>
                    <span>או ההרשמה מהירה עם</span>
                </div>

                {/* Social Login */}
                <div className="social-login">
                    <button onClick={handleGoogleLogin} className="social-btn" type="button">
                        <svg width="24" height="24" viewBox="0 0 24 24">
                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                        </svg>
                        <span>המשך עם Google</span>
                    </button>
                </div>

                {/* Login Link */}
                <div className="register-link">
                    כבר יש לך חשבון? <Link to={ROUTES.LOGIN}>התחבר עכשיו</Link>
                </div>
            </div>
        </div>
    );
};

export default Register;
