import './Login.css';
import LoginForm from "../components/LoginForm";    
import NavBarLogout from "../components/NavBarLogout";

export default function Login() {
    return (
        <>
            <NavBarLogout />
            <section className="login-page">
                <div className="login-page-container">
                    <section className="login-page-intro">
                        <h1>Welcome Back!</h1>
                        <p>Login to your account to continue!</p>
                    </section>
                    <LoginForm />
                </div>
                
            </section>
        </>
    )
}