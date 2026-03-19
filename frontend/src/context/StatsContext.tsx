import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import { getUserStats } from "../services/api";
import { useAuth } from "./AuthContext";
import type { UserStats } from "../types";

interface StatsContextType {
  stats: UserStats | null;
  isLoading: boolean;
  refreshStats: () => Promise<void>;
}

const StatsContext = createContext<StatsContextType | null>(null);

export function StatsProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshStats = useCallback(async () => {
    if (!isAuthenticated) {
      setStats(null);
      return;
    }
    setIsLoading(true);
    try {
      const data = await getUserStats();
      setStats(data);
    } catch {
      setStats(null);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      setStats(null);
      setIsLoading(false);
      return;
    }
    let cancelled = false;
    setIsLoading(true);
    getUserStats()
      .then((data) => { if (!cancelled) setStats(data); })
      .catch(() => { if (!cancelled) setStats(null); })
      .finally(() => { if (!cancelled) setIsLoading(false); });
    return () => { cancelled = true; };
  }, [isAuthenticated, authLoading]);

  return (
    <StatsContext.Provider value={{ stats, isLoading, refreshStats }}>
      {children}
    </StatsContext.Provider>
  );
}

export function useStats(): StatsContextType {
  const context = useContext(StatsContext);
  if (!context) {
    throw new Error("useStats must be used within a StatsProvider");
  }
  return context;
}
