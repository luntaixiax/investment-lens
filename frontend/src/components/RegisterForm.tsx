import axios from 'axios';
import './RegisterForm.css';
import { useForm } from 'react-hook-form';
import { useState } from 'react';

type RegisterData = {
	username: string;
	email: string;
	password: string;
}

type Message = {
	message: string;
	success: boolean;
}

export default function RegisterForm() {

	const [messageOnRegister, setMessageOnRegister] = useState<Message>({ message: '', success: false });
	const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<RegisterData>();

	async function onRegister(data: RegisterData) {
		// Simulate API call with a Promise
		// await new Promise(resolve => setTimeout(resolve, 1000));
		try {
			await axios.post('/backend/api/v1/management/register', data);
			setMessageOnRegister({
				message: `Welcome, ${data.username}!`,
				success: true
			});
		} catch (error: any) {
			if (axios.isAxiosError(error)) {
				if (error.response?.status === 520) {
					setMessageOnRegister({
						message: error.response.data.message,
						success: false
					});
				} else {
					setMessageOnRegister({
						message: `An unknown error occurred with status code: ${error.response?.status}`,
						success: false
					});
				}
			}
		} 

	}


	return (
		<form onSubmit={handleSubmit(onRegister)} className="register-form">
			<h1>Register</h1>
			<div className="register-form-row">
				<label htmlFor="username">
					<i className="fa-solid fa-user"></i>
					<span>&nbsp; User Name</span>
				</label>
				<input
					type="text"
					id="username"
					placeholder='your user name, e.g., luntaixia'
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
				<label htmlFor="email">
					<i className="fa-solid fa-envelope"></i>
					<span>&nbsp; Email</span>
				</label>
				<input
					type="email"
					id="email"
					placeholder='your email address, e.g., luntaix@ltxservice.ca'
					{...
					register(
						'email',
						{
							required: 'Email is required',
							pattern: {
								value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
								message: 'Invalid email address'
							}
						}
					)
					}
				/>
				{
					errors.email // if there is an error about the email field, then:
					&& <p className="error">‼️🙊 {errors.email.message}</p> // show the error message defined above
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
					placeholder='your strong password, e.g., 12345678'
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
						<span>&nbsp;&nbsp;Registering...</span>
					</>
				) : (
					'Register'
				)}
			</button>

			{messageOnRegister.message && (
				messageOnRegister.success ? (
					<p className="success">🥳🥳 {messageOnRegister.message} 🥳🥳</p>
				) : (
					<p className="fail">🥵🥵 {messageOnRegister.message} 🥵🥵</p>
				)
			)}

		</form>
	)
}