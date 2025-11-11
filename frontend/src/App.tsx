import './App.css'
import { Route, Routes } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import AuthProvider from './hooks/AuthContext';
import Home from './pages/Home';
import Login from './pages/Login';
import Landing from './pages/Landing';
import Register from './pages/Register';
import Market from './pages/Market';




function App() {

	return (
		<AuthProvider>
			<Routes>
				<Route path="/" element={<Landing />} />
				<Route path="/register" element={<Register />} />
				<Route path="/login" element={<Login />} />

				{/* All protected routes go inside this (except login and register) */}
				<Route path="/home" element={
					<ProtectedRoute>
						<Home />
					</ProtectedRoute>} 
				/>
				<Route path="/market" element={
					<ProtectedRoute>
						<Market />
					</ProtectedRoute>} 
				/>
			</Routes>
		</AuthProvider>
	)
}

export default App
