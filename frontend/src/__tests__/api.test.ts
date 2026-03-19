import { describe, it, expect, afterEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "../test/mocks/server";
import {
  storeTokens,
  clearTokens,
  getStoredTokens,
  authSignup,
  authLogin,
  authLogout,
  authMe,
  authDeleteAccount,
  authResendVerification,
  authVerifyEmail,
  fetchTopics,
  generateTest,
  getTest,
} from "../services/api";

// === Token Storage ===

describe("Token Storage", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("stores and retrieves tokens", () => {
    storeTokens("access-123", "refresh-456", 900);
    const tokens = getStoredTokens();
    expect(tokens.accessToken).toBe("access-123");
    expect(tokens.refreshToken).toBe("refresh-456");
    expect(tokens.expiresAt).toBeTruthy();
  });

  it("clears all tokens", () => {
    storeTokens("a", "r", 900);
    clearTokens();
    const tokens = getStoredTokens();
    expect(tokens.accessToken).toBeNull();
    expect(tokens.refreshToken).toBeNull();
    expect(tokens.expiresAt).toBeNull();
  });

  it("returns null for missing tokens", () => {
    const tokens = getStoredTokens();
    expect(tokens.accessToken).toBeNull();
    expect(tokens.refreshToken).toBeNull();
    expect(tokens.expiresAt).toBeNull();
  });

  it("computes expiration timestamp correctly", () => {
    const before = Date.now();
    storeTokens("a", "r", 900);
    const after = Date.now();
    const expiresAt = Number(getStoredTokens().expiresAt);
    // Should be ~900 seconds from now
    expect(expiresAt).toBeGreaterThanOrEqual(before + 900 * 1000);
    expect(expiresAt).toBeLessThanOrEqual(after + 900 * 1000);
  });

  it("overwrites previously stored tokens", () => {
    storeTokens("old-access", "old-refresh", 100);
    storeTokens("new-access", "new-refresh", 200);
    const tokens = getStoredTokens();
    expect(tokens.accessToken).toBe("new-access");
    expect(tokens.refreshToken).toBe("new-refresh");
  });
});

// === Runtime Validators (tested indirectly via fetchTopics / generateTest) ===
// validateTopics and validateTestResponse are internal (not exported),
// so we test them through the public API functions that use them.

describe("Runtime Validators (via fetchTopics)", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("fetchTopics succeeds with valid topic data", async () => {
    const topics = await fetchTopics();
    expect(topics).toHaveLength(1);
    expect(topics[0].id).toBe("algebra");
    expect(topics[0].name).toBe("Algebra");
    expect(topics[0].subtopics).toHaveLength(1);
  });

  it("fetchTopics throws when server returns non-array", async () => {
    server.use(
      http.get("/api/tests/topics", () => {
        return HttpResponse.json({ not: "an array" });
      })
    );
    await expect(fetchTopics()).rejects.toThrow("expected array");
  });

  it("fetchTopics throws when topic is missing id", async () => {
    server.use(
      http.get("/api/tests/topics", () => {
        return HttpResponse.json([{ name: "No ID", subtopics: [] }]);
      })
    );
    await expect(fetchTopics()).rejects.toThrow("missing id");
  });

  it("fetchTopics throws when topic is missing subtopics array", async () => {
    server.use(
      http.get("/api/tests/topics", () => {
        return HttpResponse.json([{ id: "t1", name: "T1" }]);
      })
    );
    await expect(fetchTopics()).rejects.toThrow("missing subtopics array");
  });

  it("fetchTopics throws when topic is null", async () => {
    server.use(
      http.get("/api/tests/topics", () => {
        return HttpResponse.json([null]);
      })
    );
    await expect(fetchTopics()).rejects.toThrow("expected object");
  });
});

describe("Runtime Validators (via generateTest)", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("generateTest succeeds with valid response", async () => {
    const result = await generateTest({
      topics: ["algebra"],
      difficulty: "easy",
      count: 2,
    });
    expect(result.test_id).toBe("test-123");
    expect(result.questions).toHaveLength(2);
  });

  it("generateTest throws when response is missing test_id", async () => {
    server.use(
      http.post("/api/tests/generate", () => {
        return HttpResponse.json({ questions: [] });
      })
    );
    await expect(
      generateTest({ topics: ["algebra"], difficulty: "easy", count: 1 })
    ).rejects.toThrow("missing test_id");
  });

  it("generateTest throws when response is missing questions array", async () => {
    server.use(
      http.post("/api/tests/generate", () => {
        return HttpResponse.json({ test_id: "t1" });
      })
    );
    await expect(
      generateTest({ topics: ["algebra"], difficulty: "easy", count: 1 })
    ).rejects.toThrow("missing questions array");
  });

  it("generateTest throws when response is not an object", async () => {
    server.use(
      http.post("/api/tests/generate", () => {
        return HttpResponse.json("just a string");
      })
    );
    await expect(
      generateTest({ topics: ["algebra"], difficulty: "easy", count: 1 })
    ).rejects.toThrow("expected object");
  });
});

describe("Runtime Validators (via getTest)", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("getTest succeeds with valid response", async () => {
    const result = await getTest("test-123");
    expect(result.test_id).toBe("test-123");
    expect(result.questions).toHaveLength(1);
  });

  it("getTest rejects for non-existent test", async () => {
    await expect(getTest("nonexistent")).rejects.toThrow();
  });
});

// === Auth API Functions ===

describe("Auth API — authSignup", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("returns success message", async () => {
    const result = await authSignup("new@example.com", "securepass123");
    expect(result.message).toContain("check your email");
  });
});

describe("Auth API — authLogin", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("returns tokens and user for valid credentials", async () => {
    const result = await authLogin("test@example.com", "validpass123");
    expect(result.access_token).toBe("mock-access-token");
    expect(result.refresh_token).toBe("mock-refresh-token");
    expect(result.expires_in).toBe(900);
    expect(result.user.email).toBe("test@example.com");
    expect(result.user.email_verified).toBe(true);
  });

  it("throws for invalid credentials", async () => {
    await expect(
      authLogin("wrong@example.com", "wrongpass")
    ).rejects.toThrow();
  });
});

describe("Auth API — authLogout", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("returns success message", async () => {
    const result = await authLogout();
    expect(result.message).toContain("Logged out");
  });
});

describe("Auth API — authMe", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("returns user profile when authenticated", async () => {
    storeTokens("mock-access-token", "mock-refresh-token", 900);
    const profile = await authMe();
    expect(profile.id).toBe("user-1");
    expect(profile.email).toBe("test@example.com");
    expect(profile.email_verified).toBe(true);
  });

  it("throws when not authenticated (no token stored)", async () => {
    // No token stored: request goes without Authorization header.
    // MSW handler returns 401. Response interceptor tries refresh but
    // no refresh token exists, so it fails immediately.
    await expect(authMe()).rejects.toThrow();
  });

  it("throws when token is invalid and refresh fails", async () => {
    // Store an invalid access token with a refresh token.
    // The MSW /auth/me handler returns 401 for non-matching tokens.
    // The response interceptor tries to refresh, but the default
    // MSW refresh handler also returns 401.
    storeTokens("bad-access-token", "bad-refresh-token", 900);
    await expect(authMe()).rejects.toThrow();
    // After failed refresh, tokens should be cleared
    const tokens = getStoredTokens();
    expect(tokens.accessToken).toBeNull();
    expect(tokens.refreshToken).toBeNull();
  });
});

describe("Auth API — authDeleteAccount", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("returns success message", async () => {
    const result = await authDeleteAccount();
    expect(result.message).toContain("Account deleted");
  });
});

describe("Auth API — authResendVerification", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("returns success message", async () => {
    const result = await authResendVerification("test@example.com");
    expect(result.message).toContain("verification link has been sent");
  });
});

describe("Auth API — authVerifyEmail", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("returns tokens for valid verification code", async () => {
    const result = await authVerifyEmail("test@example.com", "123456");
    expect(result.access_token).toBe("verified-access-token");
    expect(result.refresh_token).toBe("verified-refresh-token");
    expect(result.user.email).toBe("test@example.com");
    expect(result.user.email_verified).toBe(true);
  });

  it("throws for invalid verification code", async () => {
    await expect(
      authVerifyEmail("test@example.com", "wrong-code")
    ).rejects.toThrow();
  });
});

// === Request Interceptor ===

describe("Request Interceptor", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("attaches Bearer token to requests when stored", async () => {
    storeTokens("mock-access-token", "mock-refresh-token", 900);
    // authMe succeeds only when Authorization: Bearer mock-access-token is set
    const profile = await authMe();
    expect(profile.email).toBe("test@example.com");
  });

  it("does not attach Authorization header when no token is stored", async () => {
    // Without a token, the /auth/me endpoint returns 401
    await expect(authMe()).rejects.toThrow();
  });
});

// === Response Interceptor (401 refresh with mutex) ===

describe("Response Interceptor — token refresh", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("retries request after successful token refresh", async () => {
    // Start with a bad access token but a valid refresh token.
    // Override the refresh handler to succeed and return new tokens.
    storeTokens("expired-access-token", "valid-refresh-token", 900);

    server.use(
      http.post("/api/auth/refresh", () => {
        return HttpResponse.json({
          access_token: "mock-access-token",
          refresh_token: "new-refresh-token",
          expires_in: 900,
          token_type: "bearer",
        });
      })
    );

    // First call to /auth/me fails (expired-access-token != mock-access-token).
    // Interceptor refreshes, gets mock-access-token, retries => succeeds.
    const profile = await authMe();
    expect(profile.email).toBe("test@example.com");

    // Verify tokens were updated
    const tokens = getStoredTokens();
    expect(tokens.accessToken).toBe("mock-access-token");
    expect(tokens.refreshToken).toBe("new-refresh-token");
  });

  it("clears tokens and rejects when refresh fails", async () => {
    storeTokens("expired-access-token", "invalid-refresh-token", 900);

    // Default MSW refresh handler returns 401 (failure).
    await expect(authMe()).rejects.toThrow();

    // Tokens should be cleared after failed refresh
    const tokens = getStoredTokens();
    expect(tokens.accessToken).toBeNull();
    expect(tokens.refreshToken).toBeNull();
    expect(tokens.expiresAt).toBeNull();
  });

  it("does not retry more than once (prevents infinite loop)", async () => {
    storeTokens("expired-access-token", "valid-refresh-token", 900);
    let refreshCount = 0;

    server.use(
      http.post("/api/auth/refresh", () => {
        refreshCount++;
        // Return new tokens, but the access token is still "bad"
        // so the retried /auth/me will also 401.
        return HttpResponse.json({
          access_token: "still-bad-token",
          refresh_token: "new-refresh-token",
          expires_in: 900,
          token_type: "bearer",
        });
      })
    );

    // First /auth/me => 401 => refresh => retry /auth/me => 401 again.
    // The _retry flag prevents a second refresh attempt.
    await expect(authMe()).rejects.toThrow();
    expect(refreshCount).toBe(1);
  });

  it("deduplicates concurrent refresh requests (mutex)", async () => {
    storeTokens("expired-access-token", "valid-refresh-token", 900);
    let refreshCount = 0;

    server.use(
      http.post("/api/auth/refresh", () => {
        refreshCount++;
        return HttpResponse.json({
          access_token: "mock-access-token",
          refresh_token: "new-refresh-token",
          expires_in: 900,
          token_type: "bearer",
        });
      })
    );

    // Fire two concurrent requests that both get 401.
    // The mutex should ensure only one refresh call is made.
    const [profile1, profile2] = await Promise.all([authMe(), authMe()]);

    expect(profile1.email).toBe("test@example.com");
    expect(profile2.email).toBe("test@example.com");
    expect(refreshCount).toBe(1);
  });
});
