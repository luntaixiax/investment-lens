import './Landing.css';
import NavBarLogout from "../components/NavBarLogout";

// page when log out and landing page
export default function Landing() {
    return (
        <>
            <NavBarLogout />
            <section className="landing-page">
                <div className="landing-page-container">
                    <h1>Welcome to Investment Lens</h1>
                </div>
            </section>
        </>
    )
}