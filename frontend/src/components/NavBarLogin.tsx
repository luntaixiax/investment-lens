import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function NavBarLogin() {
    const { logout } = useAuth();
    const navigate = useNavigate();

    async function handleLogout() {
        const result = await logout();
        if (result.is_success) {
            navigate('/login');
        }
    }

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/home" className="navbar-logo">
                    <img src="/images/icons/LTX - logo.png" alt="Investment Lens" className="navbar-logo-image" />
                    <span>Investment Lens</span>
                </Link>
                <div className="navbar-menu">
                    <Link to="/settings" className="navbar-link">
                        <i className="fa-solid fa-gear"></i>
                        <span>Settings</span>
                    </Link>
                    <button onClick={handleLogout} className="navbar-link">
                        <i className="fa-solid fa-right-from-bracket"></i>
                        <span>Logout</span>
                    </button>
                </div>
            </div>
        </nav>
    )
}