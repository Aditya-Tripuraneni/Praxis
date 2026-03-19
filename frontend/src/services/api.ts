import axios from "axios";
import type { TopicInfo, GenerateRequest, TestResponse, AuthResponse, AuthMessage, UserProfile, RefreshResponse, SubscriptionStatus, CheckoutSessionResponse, CancelSubscriptionResponse, UserStats, SavedTestSummary, SavedTest } from "../types";

// === Token Storage ===

const TOKEN_KEYS = {
  access: "pg_access_token",
  refresh: "pg_refresh_token",
  expiresAt: "pg_token_expires_at",
} as const;

export function getStoredTokens() {
  return {
    accessToken: localStorage.getItem(TOKEN_KEYS.access),
    refreshToken: localStorage.getItem(TOKEN_KEYS.refresh),
    expiresAt: localStorage.getItem(TOKEN_KEYS.expiresAt),
  };
}

export function storeTokens(accessToken: string, refreshToken: string, expiresIn: number) {
  const expiresAt = String(Date.now() + expiresIn * 1000);
  localStorage.setItem(TOKEN_KEYS.access, accessToken);
  localStorage.setItem(TOKEN_KEYS.refresh, refreshToken);
  localStorage.setItem(TOKEN_KEYS.expiresAt, expiresAt);
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEYS.access);
  localStorage.removeItem(TOKEN_KEYS.refresh);
  localStorage.removeItem(TOKEN_KEYS.expiresAt);
}

const client = axios.create({
  baseURL: "/api",
});

// === Request Interceptor — attach Bearer token ===

client.interceptors.request.use((config) => {
  const { accessToken } = getStoredTokens();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// === TypeScript augmentation for retry flag ===
declare module "axios" {
  interface InternalAxiosRequestConfig {
    _retry?: boolean;
  }
}

// === Response Interceptor — refresh on 401 with mutex ===

let refreshPromise: Promise<boolean> | null = null;

async function attemptRefresh(): Promise<boolean> {
  const { refreshToken } = getStoredTokens();
  if (!refreshToken) return false;

  try {
    const response = await axios.post("/api/auth/refresh", {
      refresh_token: refreshToken,
    });

    const data = response.data as RefreshResponse;
    storeTokens(data.access_token, data.refresh_token, data.expires_in);
    return true;
  } catch {
    clearTokens();
    return false;
  }
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (!refreshPromise) {
        refreshPromise = attemptRefresh().finally(() => {
          refreshPromise = null;
        });
      }

      const success = await refreshPromise;
      if (success) {
        const { accessToken } = getStoredTokens();
        originalRequest.headers.Authorization = `Bearer ${accessToken}`;
        return client(originalRequest);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Runtime validation guards.
 * TypeScript types are compile-time only — these catch malformed API responses
 * at the boundary instead of letting them crash deep in component code.
 */

function validateTopics(data: unknown): TopicInfo[] {
  if (!Array.isArray(data)) {
    throw new Error("Invalid topics response: expected array");
  }
  for (const item of data) {
    if (typeof item !== "object" || item === null) {
      throw new Error("Invalid topic: expected object");
    }
    if (typeof (item as TopicInfo).id !== "string") {
      throw new Error("Invalid topic: missing id");
    }
    if (!Array.isArray((item as TopicInfo).subtopics)) {
      throw new Error("Invalid topic: missing subtopics array");
    }
  }
  return data as TopicInfo[];
}

function validateTestResponse(data: unknown): TestResponse {
  if (typeof data !== "object" || data === null) {
    throw new Error("Invalid test response: expected object");
  }
  const obj = data as TestResponse;
  if (typeof obj.test_id !== "string") {
    throw new Error("Invalid test response: missing test_id");
  }
  if (!Array.isArray(obj.questions)) {
    throw new Error("Invalid test response: missing questions array");
  }
  return obj;
}

function validateAuthResponse(data: unknown): AuthResponse {
  if (typeof data !== "object" || data === null) {
    throw new Error("Invalid auth response: expected object");
  }
  const obj = data as AuthResponse;
  if (typeof obj.access_token !== "string") {
    throw new Error("Invalid auth response: missing access_token");
  }
  if (typeof obj.refresh_token !== "string") {
    throw new Error("Invalid auth response: missing refresh_token");
  }
  if (!obj.user || typeof obj.user.email !== "string") {
    throw new Error("Invalid auth response: missing user");
  }
  return obj;
}

function validateUserProfile(data: unknown): UserProfile {
  if (typeof data !== "object" || data === null) {
    throw new Error("Invalid user profile: expected object");
  }
  const obj = data as UserProfile;
  if (typeof obj.id !== "string") {
    throw new Error("Invalid user profile: missing id");
  }
  if (typeof obj.email !== "string") {
    throw new Error("Invalid user profile: missing email");
  }
  return obj;
}

function validateCheckoutSession(data: unknown): CheckoutSessionResponse {
  if (typeof data !== "object" || data === null) {
    throw new Error("Invalid checkout response: expected object");
  }
  if (typeof (data as CheckoutSessionResponse).url !== "string") {
    throw new Error("Invalid checkout response: missing url");
  }
  return data as CheckoutSessionResponse;
}

function validateSubscriptionStatus(data: unknown): SubscriptionStatus {
  if (typeof data !== "object" || data === null) {
    throw new Error("Invalid subscription status: expected object");
  }
  const d = data as Record<string, unknown>;
  if (typeof d.status !== "string") {
    throw new Error("Invalid subscription status: missing status");
  }
  if (typeof d.is_active !== "boolean") {
    throw new Error("Invalid subscription status: missing is_active");
  }
  return {
    status: d.status as string,
    is_active: d.is_active as boolean,
    current_period_end: typeof d.current_period_end === "string" ? d.current_period_end : null,
    plan: typeof d.plan === "string" ? d.plan : null,
  };
}

/**
 * Extract a user-facing error message from an axios error response.
 * Handles FastAPI's { detail: "string" } and { detail: [{msg: "..."}] } formats.
 */
export function extractErrorDetail(error: unknown, fallback: string): string {
  if (
    typeof error === "object" &&
    error !== null &&
    "response" in error
  ) {
    const resp = (error as { response?: { data?: { detail?: unknown } } }).response;
    const detail = resp?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      // FastAPI 422 validation errors: [{ loc: [...], msg: "...", type: "..." }]
      const first = detail[0];
      if (typeof first === "object" && first !== null && "msg" in first) {
        return String(first.msg);
      }
    }
  }
  return fallback;
}

export async function fetchSampleTest(
  topics: string = "algebra",
  difficulty: string = "easy",
  count: number = 5,
): Promise<TestResponse> {
  const response = await client.get("/sample-test", {
    params: { topics, difficulty, count },
  });
  return validateTestResponse(response.data);
}

export async function fetchTopics(): Promise<TopicInfo[]> {
  const response = await client.get("/tests/topics");
  return validateTopics(response.data);
}

export async function generateTest(
  req: GenerateRequest
): Promise<TestResponse> {
  const response = await client.post("/tests/generate", req);
  return validateTestResponse(response.data);
}

export async function getTest(id: string): Promise<TestResponse> {
  const response = await client.get(`/tests/${id}`);
  return validateTestResponse(response.data);
}

export async function downloadPdf(
  id: string,
  includeAnswers: boolean,
  includeSolutions: boolean = false
): Promise<void> {
  const response = await client.get(`/tests/${id}/pdf`, {
    params: { include_answers: includeAnswers, include_solutions: includeSolutions },
    responseType: "blob",
  });

  const blob = new Blob([response.data], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `test-${id}${includeAnswers ? "-with-answers" : ""}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// === Auth API ===

export async function authSignup(email: string, password: string): Promise<AuthMessage> {
  const response = await client.post("/auth/signup", { email, password });
  return response.data;
}

export async function authLogin(email: string, password: string): Promise<AuthResponse> {
  const response = await client.post("/auth/login", { email, password });
  return validateAuthResponse(response.data);
}

export async function authLogout(): Promise<AuthMessage> {
  const response = await client.post("/auth/logout");
  return response.data;
}

export async function authMe(): Promise<UserProfile> {
  const response = await client.get("/auth/me");
  return validateUserProfile(response.data);
}

export async function authDeleteAccount(): Promise<AuthMessage> {
  const response = await client.delete("/auth/account");
  return response.data;
}

export async function authResendVerification(email: string): Promise<AuthMessage> {
  const response = await client.post("/auth/resend-verification", { email });
  return response.data;
}

export async function authVerifyEmail(email: string, token: string): Promise<AuthResponse> {
  const response = await client.post("/auth/verify-email", { email, token });
  return validateAuthResponse(response.data);
}

export async function authForgotPassword(email: string): Promise<AuthMessage> {
  const response = await client.post("/auth/forgot-password", { email });
  return response.data;
}

export async function authResetPassword(
  email: string,
  token: string,
  new_password: string,
): Promise<AuthResponse> {
  const response = await client.post("/auth/reset-password", { email, token, new_password });
  return validateAuthResponse(response.data);
}

// === Billing API ===

export async function createCheckoutSession(plan: 'student' | 'tutor'): Promise<CheckoutSessionResponse> {
  const response = await client.post("/billing/create-checkout-session", { plan });
  return validateCheckoutSession(response.data);
}

export async function getSubscriptionStatus(): Promise<SubscriptionStatus> {
  const response = await client.get("/billing/subscription-status");
  return validateSubscriptionStatus(response.data);
}

export async function cancelSubscription(): Promise<CancelSubscriptionResponse> {
  const response = await client.post("/billing/cancel-subscription");
  return response.data;
}

// === Stats API ===

function validateUserStats(data: unknown): UserStats {
  if (!data || typeof data !== "object") {
    throw new Error("Invalid stats response");
  }
  const d = data as Record<string, unknown>;
  if (typeof d.tests_generated !== "number") {
    throw new Error("Invalid stats: missing tests_generated");
  }
  if (typeof d.questions_generated !== "number") {
    throw new Error("Invalid stats: missing questions_generated");
  }
  return d as unknown as UserStats;
}

export async function getUserStats(): Promise<UserStats> {
  const response = await client.get("/stats/me");
  return validateUserStats(response.data);
}

export async function saveTimerDuration(duration: number): Promise<void> {
  await client.put("/stats/timer", { duration });
}

// === Saved Tests ===

export async function getSavedTests(): Promise<SavedTestSummary[]> {
  const response = await client.get("/saved-tests");
  if (!Array.isArray(response.data)) throw new Error("Invalid saved tests response");
  return response.data as SavedTestSummary[];
}

export async function saveTest(data: {
  test_name: string;
  config: { topics: string[]; difficulty: string; count: number };
  seed: number;
  questions: Array<Record<string, unknown>>;
}): Promise<SavedTestSummary> {
  const response = await client.post("/saved-tests", data);
  return response.data as SavedTestSummary;
}

export async function replaySavedTest(id: string): Promise<SavedTest> {
  const response = await client.get(`/saved-tests/${id}/replay`);
  return response.data as SavedTest;
}

export async function renameSavedTest(id: string, test_name: string): Promise<SavedTestSummary> {
  const response = await client.patch(`/saved-tests/${id}`, { test_name });
  return response.data as SavedTestSummary;
}

export async function deleteSavedTest(id: string): Promise<void> {
  await client.delete(`/saved-tests/${id}`);
}
