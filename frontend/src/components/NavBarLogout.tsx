import { Link } from 'react-router-dom';
import './NavBarLogout.css';

export default function NavbarLogout() {
    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/home" className="navbar-logo">
                    <img src="/images/icons/LTX - logo.png" alt="Investment Lens" className="navbar-logo-image" />
                    <span>Investment Lens</span>
                </Link>
                <div className="navbar-menu">
                    <Link to="/register" className="navbar-link">
                        <i className="fa-solid fa-user-plus"></i>
                        <span>Register</span>
                    </Link>
                    <Link to="/login" className="navbar-link">
                        <i className="fa-solid fa-sign-in-alt"></i>
                        <span>Login</span>
                    </Link>
                </div>
            </div>
        </nav>
    );
}

