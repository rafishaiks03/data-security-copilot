import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import {
  clearToken,
  isAuthenticated,
} from "../api/client";

interface AuthContextValue {
  authenticated: boolean;
  logout: () => void;
  refreshAuth: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(
  undefined,
);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [authenticated, setAuthenticated] = useState(
    isAuthenticated(),
  );

  function refreshAuth() {
    setAuthenticated(isAuthenticated());
  }

  function logout() {
    clearToken();
    setAuthenticated(false);
  }

  useEffect(() => {
    function handleStorageChange() {
      refreshAuth();
    }

    function handleAuthLogout() {
      setAuthenticated(false);
    }

    window.addEventListener(
      "storage",
      handleStorageChange,
    );

    window.addEventListener(
      "auth:logout",
      handleAuthLogout,
    );

    return () => {
      window.removeEventListener(
        "storage",
        handleStorageChange,
      );

      window.removeEventListener(
        "auth:logout",
        handleAuthLogout,
      );
    };
  }, []);

  return (
    <AuthContext.Provider
      value={{
        authenticated,
        logout,
        refreshAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider",
    );
  }

  return context;
}