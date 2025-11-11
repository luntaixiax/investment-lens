import './LoginForm.css';
import { useForm } from 'react-hook-form';
import { useState } from 'react';
import { useNavigate } from "react-router-dom";
import axios from 'axios';
import { useAuth } from '../hooks/AuthContext';

type LoginData = {
	username: string;
	password: string;
}

type Message = {
	message: string;
	success: boolean;
}

export default function LoginForm() {

    const navigate = useNavigate();
    const [messageOnLogin, setMessageOnLogin] = useState<Message>({ message: '', success: false });
    // the return value is register, but not that register we understand.
    const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginData>();

    const { login } = useAuth();

    async function onLogin(data: LoginData) {

        const result = await login(data);
        if (result.is_success) {
            setMessageOnLogin({
                message: result.message,
                success: true
            });

            setTimeout(() => {
                navigate("/home"); // redirect to homepage
            }, 1000); // wait 1 second before redirecting
        } else {
            setMessageOnLogin({
                message: result.message,
                success: false
            });
        }
    }

	return (
		<form onSubmit={handleSubmit(onLogin)} className="register-form">
			<h1>Login</h1>
			<div className="register-form-row">
				<label htmlFor="username">
					<i className="fa-solid fa-user"></i>
					<span>&nbsp; User Name</span>
				</label>
				<input
					type="text"
					id="username"
					placeholder='enter your user name'
					{...
                        register(
						'username', // the name of the field
						// below are the validation rules for the username field
						{
							required: 'Username is required',
							minLength: {
								value: 3,
								message: 'Username must be at least 3 characters long'
							},
							maxLength: {
								value: 20,
								message: 'Username must be at most 20 characters long'
							},
							pattern: {
								value: /^[a-zA-Z0-9]+$/,
								message: 'Username must be only alphanumeric'
							}
						}
					)
					}
				/>
				{
					errors.username // if there is an error about the username field, then:
					&& <p className="error">‼️🙊 {errors.username.message}</p> // show the error message defined above
				}
			</div>

			<div className="register-form-row">
				<label htmlFor="password">
					<i className="fa-solid fa-lock"></i>
					<span>&nbsp; Password</span>
				</label>
				<input
					type="password"
					id="password"
					placeholder='enter your password'
					{...register(
						'password',
						{
							required: 'Password is required',
							minLength: {
								value: 8,
								message: 'Password must be at least 8 characters long'
							},
							maxLength: {
								value: 20,
								message: 'Password must be at most 20 characters long'
							}
						}
					)}
				/>
				{
					errors.password // if there is an error about the password field, then:
					&& <p className="error">‼️🙊 {errors.password.message}</p> // show the error message defined above
				}
			</div>


			<button
				className="register-form-button"
				type="submit"
				// if the form is submitting, then show 'Submitting...' else show 'Submit'
				disabled={isSubmitting}
			>
				{isSubmitting ? (
					<>
						<i className="fa-solid fa-spinner fa-spin"></i>
						<span>&nbsp;&nbsp;Logging in...</span>
					</>
				) : (
					'Login'
				)}
			</button>

            {(
				messageOnLogin.success ? (
					<p className="success">🥳🥳 {messageOnLogin.message} 🥳🥳</p>
				) : (
					<p className="fail">🥵🥵 {messageOnLogin.message} 🥵🥵</p>
				)
			)}


		</form>
	)
}