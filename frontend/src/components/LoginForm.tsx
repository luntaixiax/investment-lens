import './LoginForm.css';
import { useForm } from 'react-hook-form';
import { useState } from 'react';
import axios from 'axios';

type LoginData = {
	username: string;
	password: string;
}

type Message = {
	message: string;
	success: boolean;
}

export default function LoginForm() {

    const [messageOnLogin, setMessageOnLogin] = useState<Message>({ message: '', success: false });
    // the return value is register, but not that register we understand.
    const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginData>();

    async function onLogin(data: LoginData) {
        try {
            const formData = new URLSearchParams();
            formData.append('username', data.username);
            formData.append('password', data.password);
            
            await axios.post('/backend/api/v1/management/login', formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });
            setMessageOnLogin({
                message: `Welcome back, ${data.username}!`,
                success: true
            });
        } catch (error) {
            if (axios.isAxiosError(error)) {
				if (error.response?.status === 403) {
					setMessageOnLogin({
						message: error.response.data.message,
						success: false
					});
				} else if (error.response?.status === 429) {
					setMessageOnLogin({
						message: error.response.data.message,
						success: false
					});
				} else {
					setMessageOnLogin({
						message: `An unknown error occurred with status code: ${error.response?.status}`,
						success: false
					});
				}
			}
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