import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import type { UserProfile } from "../types";
import {
  authLogin,
  authSignup,
  authLogout,
  authMe,
  authDeleteAccount,
  authResendVerification,
  storeTokens,
  clearTokens,
  getStoredTokens,
} from "../services/api";
import { signInWithGoogle } from "../services/supabase";

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithTokens: (accessToken: string, refreshToken: string, expiresIn: number) => Promise<void>;
  register: (email: string, password: string) => Promise<string>;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  deleteAccount: () => Promise<void>;
  resendVerification: (email: string) => Promise<string>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = user !== null;

  useEffect(() => {
    async function checkAuth() {
      const { accessToken } = getStoredTokens();
      if (!accessToken) {
        setIsLoading(false);
        return;
      }

      try {
        const profile = await authMe();
        setUser(profile);
      } catch {
        clearTokens();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    checkAuth();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const result = await authLogin(email, password);
    storeTokens(result.access_token, result.refresh_token, result.expires_in);
    setUser(result.user);
  }, []);

  const loginWithTokensFn = useCallback(async (accessToken: string, refreshToken: string, expiresIn: number) => {
    storeTokens(accessToken, refreshToken, expiresIn);
    try {
      const profile = await authMe();
      setUser(profile);
    } catch {
      clearTokens();
      throw new Error("Failed to verify session");
    }
  }, []);

  const register = useCallback(async (email: string, password: string): Promise<string> => {
    const result = await authSignup(email, password);
    return result.message;
  }, []);

  const loginWithGoogleFn = useCallback(async () => {
    const { error } = await signInWithGoogle();
    if (error) {
      throw new Error(error.message);
    }
  }, []);

  const logoutFn = useCallback(async () => {
    try {
      await authLogout();
    } catch {
      // Clear local state even if API call fails
    }
    clearTokens();
    setUser(null);
  }, []);

  const deleteAccountFn = useCallback(async () => {
    await authDeleteAccount();
    clearTokens();
    setUser(null);
  }, []);

  const resendVerificationFn = useCallback(async (email: string): Promise<string> => {
    const result = await authResendVerification(email);
    return result.message;
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        login,
        loginWithTokens: loginWithTokensFn,
        register,
        loginWithGoogle: loginWithGoogleFn,
        logout: logoutFn,
        deleteAccount: deleteAccountFn,
        resendVerification: resendVerificationFn,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
