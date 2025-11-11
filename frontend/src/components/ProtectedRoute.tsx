import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/AuthContext";

type props = {
	children: React.ReactNode
}

export default function ProtectedRoute({ children }: props) {
	const { user, isLoading } = useAuth();

	// Show loading spinner while checking authentication
	if (isLoading) {
		return <p>Loading...</p>;
	}

	// If not logged in, redirect to login page (only after loading is complete)
	if (!user) {
		return <Navigate to="/login" replace />;
	}

	return children;
}
