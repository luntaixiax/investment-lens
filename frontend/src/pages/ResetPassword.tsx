import './ResetPassword.css';
import NavBarLogout from "../components/NavBarLogout";
import { useForm } from 'react-hook-form';
import axios from 'axios';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

type ResetPasswordData = {
    email: string;
}

type ResetPasswordTokenData = {
    token: string;
    new_password: string;
}

export default function ResetPassword() {

    const navigate = useNavigate();

    const {
        register: registerEmail,
        handleSubmit: handleSubmitEmail,
        formState: { errors: errorsEmail, isSubmitting: isSubmittingEmail }
    } = useForm<ResetPasswordData>();

    const [emailSent, setEmailSent] = useState<boolean | null>(null);

    async function onRequestResetPassword(data: ResetPasswordData) {
        try {
            await axios.post(`/backend/api/v1/management/request_reset_password?email=${data.email}`);
            setEmailSent(true);
        } catch (error) {
            if (axios.isAxiosError(error)) {
                if (error.response?.status === 521) {
                    setEmailSent(false);
                } else {
                    setEmailSent(false);
                }
            }
        }
    }

    const {
        register: registerToken,
        handleSubmit: handleSubmitToken,
        formState: { errors: errorsToken, isSubmitting: isSubmittingToken }
    } = useForm<ResetPasswordTokenData>();

    const [resetPasswordSuccess, setResetPasswordSuccess] = useState<boolean | null>(null);

    async function onResetPassword(data: ResetPasswordTokenData) {
        try {
            await axios.post(`/backend/api/v1/management/reset_password?token=${data.token}&new_password=${data.new_password}`);
            setResetPasswordSuccess(true);
            setTimeout(() => {
                navigate("/login");
            }, 1000);
        } catch (error) {
            if (axios.isAxiosError(error)) {
                if (error.response?.status === 403) {
                    setResetPasswordSuccess(false);
                } else {
                    setResetPasswordSuccess(null);
                }
            }
        }
    }


    return (
        <>
            <NavBarLogout />
            <section className="reset-password-page">

                <form onSubmit={handleSubmitEmail(onRequestResetPassword)} className="register-form reset-password-form">
                    <h1>Forget your password?</h1>
                    <img src="/images/backgrounds/wallhaven-d6eedl.png" alt="Reset Password" className="reset-password-image" />
                    <div className="register-form-row">
                        <label htmlFor="email">
                            <i className="fa-solid fa-envelope"></i>
                            <span>&nbsp; Enter your email below to reset your password.</span>
                        </label>
                        <input
                            id='email'
                            type="email"
                            placeholder="Email"
                            disabled={emailSent === true}
                            {...
                            registerEmail(
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
                            errorsEmail.email // if there is an error about the email field, then:
                            && <p className="error">‼️🙊 {errorsEmail.email.message}</p> // show the error message defined above
                        }



                        {
                            emailSent ? (<>
                                <p className="success">🥳🥳 Email sent! Check your inbox and paste the token below to reset your password. 🥳🥳</p>

                            </>)
                                : (<>
                                    <button
                                        className="register-form-button"
                                        type="submit"
                                        disabled={isSubmittingEmail}
                                    >
                                        {isSubmittingEmail ? 'Submitting...' : 'Send Reset Instruction'}
                                    </button>
                                    {emailSent === false && <p className="fail">🥵🥵 Email not exists or invalid! 🥵🥵</p>}
                                </>
                                )
                        }
                    </div>
                </form>


                {
                    emailSent === true && (<>
                        <form onSubmit={handleSubmitToken(onResetPassword)} className="register-form reset-password-form">
                            <div className="register-form-row">
                                <label htmlFor="token">
                                    <i className="fa-solid fa-key"></i>
                                    <span>&nbsp; Token</span>
                                </label>
                                <textarea
                                    id='token'
                                    placeholder="Paste the token here"
                                    className="reset-password-token-input"
                                    {...registerToken(
                                        'token',
                                        {
                                            required: 'Token is required'
                                        }
                                    )}
                                />
                                {
                                    errorsToken.token && <p className="error">‼️🙊 {errorsToken.token.message}</p>
                                }
                            </div>
                            <div className="register-form-row">
                                <label htmlFor="new-password">
                                    <i className="fa-solid fa-lock"></i>
                                    <span>&nbsp; New Password</span>
                                </label>
                                <input
                                    id='new-password'
                                    type="password"
                                    placeholder="New Password"
                                    {...registerToken(
                                        'new_password',
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
                                    errorsToken.new_password && <p className="error">‼️🙊 {errorsToken.new_password.message}</p>
                                }
                            </div>
                            <button
                                className="register-form-button"
                                type="submit"
                                disabled={isSubmittingToken}
                            >
                                {isSubmittingToken ? 'Submitting...' : 'Reset Password'}
                            </button>
                            {resetPasswordSuccess === false && <p className="fail">🥵🥵 Access token is invalid or expired! 🥵🥵</p>}
                            {resetPasswordSuccess === true && <p className="success">🥳🥳 Reset password successful! 🥳🥳</p>}
                        </form>
                    </>)
                }

            </section>
        </>
    )
}