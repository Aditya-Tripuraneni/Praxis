import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import { getSubscriptionStatus, createCheckoutSession, cancelSubscription } from "../services/api";
import { useAuth } from "./AuthContext";
import type { SubscriptionStatus } from "../types";

interface SubscriptionContextType {
  subscription: SubscriptionStatus | null;
  isSubscribed: boolean;
  isLoading: boolean;
  plan: string | null;
  isTutor: boolean;
  subscribe: (plan: 'student' | 'tutor') => Promise<void>;
  cancelSub: () => Promise<void>;
  refreshStatus: () => Promise<void>;
}

const SubscriptionContext = createContext<SubscriptionContextType | null>(null);

export function SubscriptionProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshStatus = useCallback(async () => {
    if (!isAuthenticated) {
      setSubscription(null);
      return;
    }
    setIsLoading(true);
    try {
      const status = await getSubscriptionStatus();
      setSubscription(status);
    } catch {
      setSubscription(null);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      setSubscription(null);
      setIsLoading(false);
      return;
    }
    let cancelled = false;
    setIsLoading(true);
    getSubscriptionStatus()
      .then((status) => { if (!cancelled) setSubscription(status); })
      .catch(() => { if (!cancelled) setSubscription(null); })
      .finally(() => { if (!cancelled) setIsLoading(false); });
    return () => { cancelled = true; };
  }, [isAuthenticated, authLoading]);

  const subscribe = useCallback(async (plan: 'student' | 'tutor') => {
    const session = await createCheckoutSession(plan);
    if (!session.url.startsWith("https://checkout.stripe.com/")) {
      throw new Error("Invalid checkout URL");
    }
    window.location.href = session.url;
  }, []);

  const cancelSub = useCallback(async () => {
    await cancelSubscription();
    await refreshStatus();
  }, [refreshStatus]);

  const isSubscribed = subscription?.is_active ?? false;
  const plan = subscription?.plan ?? null;
  const isTutor = isSubscribed && plan === 'tutor';

  return (
    <SubscriptionContext.Provider value={{ subscription, isSubscribed, isLoading, plan, isTutor, subscribe, cancelSub, refreshStatus }}>
      {children}
    </SubscriptionContext.Provider>
  );
}

export function useSubscription(): SubscriptionContextType {
  const context = useContext(SubscriptionContext);
  if (!context) {
    throw new Error("useSubscription must be used within a SubscriptionProvider");
  }
  return context;
}
