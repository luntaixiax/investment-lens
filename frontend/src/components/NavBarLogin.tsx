import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/AuthContext';
import { useClickOutside } from '../hooks/ClickOutSide';

export default function NavBarLogin() {
    const { logout } = useAuth();
    const navigate = useNavigate();
    const { dropdownRef, isOpen, setIsOpen } = useClickOutside<HTMLDivElement>(true);

    async function handleLogout() {
        const result = await logout();
        if (result.is_success) {
            navigate('/login');
        }
        setIsOpen(false);
    }

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/home" className="navbar-logo">
                    <img src="/images/icons/LTX - logo.png" alt="Investment Lens" className="navbar-logo-image" />
                    <span>Investment Lens</span>
                </Link>
                <div className="navbar-menu" ref={dropdownRef}>
                    <button 
                        className="navbar-user-menu-button"
                        onClick={() => setIsOpen(!isOpen)}
                        aria-haspopup="true"
                        aria-expanded={isOpen}
                    >
                        <i className="fa-solid fa-user-circle"></i>
                        <i className={`fa-solid fa-chevron-${isOpen ? 'up' : 'down'}`}></i>
                    </button>
                    {isOpen && (
                        <div className="navbar-dropdown-menu">
                            <Link 
                                to="/settings" 
                                className="navbar-dropdown-item"
                                onClick={() => setIsOpen(false)}
                            >
                                <i className="fa-solid fa-gear"></i>
                                <span>Settings</span>
                            </Link>
                            <button 
                                onClick={handleLogout} 
                                className="navbar-dropdown-item"
                            >
                                <i className="fa-solid fa-right-from-bracket"></i>
                                <span>Logout</span>
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    )
}