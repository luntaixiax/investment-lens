import { createContext, useContext, useState, useEffect } from "react";
import axios from 'axios';

type props = {
    children: React.ReactNode
}

type User = {
    user_id: string;
    username: string;
    is_admin: boolean;
}

type LoginData = {
    username: string;
    password: string;
}

type LoginOutResult = {
    is_success: boolean;
    message: string;
}

const AuthContext = createContext<{
    user: User | null;
    isLoading: boolean;
    login: (data: LoginData) => Promise<LoginOutResult>;
    logout: () => Promise<LoginOutResult>;
}>({
    user: null,
    isLoading: true,
    login: async () => ({ is_success: false, message: '' }),
    logout: async () => ({ is_success: false, message: '' }),
});

export default function AuthProvider({ children }: props) {

    // record the logged in user
    const [user, setUser] = useState<User | null>(null);
    // if the user is loading, show a loading spinner
    const [isLoading, setIsLoading] = useState<boolean>(true);

    // fetch the user on initial page load or refresh (session)
    useEffect(
        () => {
            async function fetchUser() {
                try {
                    const response = await axios.get(
                        '/backend/api/v1/management/check_login',
                        {
                            withCredentials: true,
                        }
                    );
                    if (response.status === 200) {
                        setUser(response.data as User);
                    } else {
                        setUser(null);
                    }
                } catch (error) {
                    // If check_login fails (e.g., not authenticated), set user to null
                    setUser(null);
                } finally {
                    // Always set loading to false, even if there's an error
                    setIsLoading(false);
                }
            }

            fetchUser();
        }, [] // only run once on initial page load
    );

    async function login(data: LoginData): Promise<LoginOutResult> {
        try {
            const formData = new URLSearchParams();
            formData.append('username', data.username);
            formData.append('password', data.password);
            await axios.post(
                '/backend/api/v1/management/login',
                formData,
                { withCredentials: true,
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }
            );

            // fetch the user
            const userResponse = await axios.get(
                '/backend/api/v1/management/check_login',
                { withCredentials: true }
            );
            if (userResponse.status === 200) {
                setUser(userResponse.data as User);
            } else {
                setUser(null);
            }
            setIsLoading(false);

            return {
                is_success: true,
                message: `Welcome back, ${userResponse.data.username}!`
            }
        } catch (error) {
            if (axios.isAxiosError(error)) {
                if (error.response?.status === 403) {
                    return {
                        is_success: false,
                        message: error.response.data.message
                    }
                } else if (error.response?.status === 429) {
                    return {
                        is_success: false,
                        message: error.response.data.message
                    }
                } else {
                    return {
                        is_success: false,
                        message: `An error occurred with status code: ${error.response?.status}`
                    }
                }
            }
            return {
                is_success: false,
                message: `An unknown error occurred`
            }
        }
    }


    async function logout(): Promise<LoginOutResult> {
        try {
            await axios.post(
                '/backend/api/v1/management/logout',
                { withCredentials: true }
            );
            setUser(null);
            setIsLoading(false);
            return {
                is_success: true,
                message: 'Logout successful'
            }
        } catch (error) {
            // Even if logout fails, clear user state and stop loading
            setUser(null);
            setIsLoading(false);
            return {
                is_success: false,
                message: `An unknown error occurred`
            }
        }
    }

    return (
        <AuthContext.Provider value={{ user, isLoading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    // custom hook to get the auth state
    return useContext(AuthContext);
}