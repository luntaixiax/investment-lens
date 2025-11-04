import './Register.css';
import RegisterForm from "../components/RegisterForm";
import NavBarLogout from "../components/NavBarLogout";

export default function Register() {
    return (
        <>
            <NavBarLogout />
            <section className="register-page">
                <div className="register-page-container">
                    <section className="register-page-intro">
                        <h1>Welcome Welcome!</h1>
                        <p>Register to get started with your investment journey!</p>
                    </section>
                    <RegisterForm />
                </div>
                
            </section>
        </>
    )
}