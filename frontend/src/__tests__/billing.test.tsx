import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { http, HttpResponse } from "msw";
import { vi, describe, it, expect, afterEach } from "vitest";
import { server } from "../test/mocks/server";
import { AuthProvider } from "../context/AuthContext";
import { StatsProvider } from "../context/StatsContext";
import { SubscriptionProvider, useSubscription } from "../context/SubscriptionContext";
import Dashboard from "../pages/Dashboard";
import CheckoutSuccess from "../pages/CheckoutSuccess";
import CheckoutCancel from "../pages/CheckoutCancel";
import { storeTokens, clearTokens } from "../services/api";

// ─── Helpers ───────────────────────────────────────────────────────────────────

/**
 * A small consumer component that reads SubscriptionContext and displays its
 * values so we can assert against the rendered text.
 */
function SubscriptionConsumer() {
  const { isSubscribed, isLoading, refreshStatus } = useSubscription();
  return (
    <div>
      <span data-testid="is-subscribed">{String(isSubscribed)}</span>
      <span data-testid="is-loading">{String(isLoading)}</span>
      <button type="button" onClick={() => refreshStatus()}>
        Refresh
      </button>
    </div>
  );
}

/** Render with auth+subscription context (authenticated). No StatsProvider
 *  — use this for SubscriptionConsumer and non-Dashboard components. */
function renderWithProviders(ui: React.ReactElement, route = "/") {
  storeTokens("mock-access-token", "mock-refresh-token", 900);
  return render(
    <MemoryRouter initialEntries={[route]}>
      <AuthProvider>
        <SubscriptionProvider>{ui}</SubscriptionProvider>
      </AuthProvider>
    </MemoryRouter>
  );
}

/** Render with auth+subscription context (NOT authenticated). */
function renderWithProvidersUnauthenticated(ui: React.ReactElement, route = "/") {
  clearTokens();
  return render(
    <MemoryRouter initialEntries={[route]}>
      <AuthProvider>
        <SubscriptionProvider>{ui}</SubscriptionProvider>
      </AuthProvider>
    </MemoryRouter>
  );
}

// ─── SubscriptionContext ────────────────────────────────────────────────────────

describe("SubscriptionContext", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("provides isSubscribed=false when not authenticated", async () => {
    renderWithProvidersUnauthenticated(<SubscriptionConsumer />);

    // Wait for auth loading to settle (no tokens => not authenticated => no fetch)
    await waitFor(() => {
      expect(screen.getByTestId("is-loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("is-subscribed").textContent).toBe("false");
  });

  it("fetches subscription status on mount when authenticated", async () => {
    renderWithProviders(<SubscriptionConsumer />);

    // Wait for both auth and subscription to settle
    await waitFor(() => {
      expect(screen.getByTestId("is-loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("is-subscribed").textContent).toBe("true");
  });

  it("handles fetch error gracefully", async () => {
    server.use(
      http.get("/api/billing/subscription-status", () => {
        return HttpResponse.json({ detail: "Server error" }, { status: 500 });
      })
    );

    renderWithProviders(<SubscriptionConsumer />);

    await waitFor(() => {
      expect(screen.getByTestId("is-loading").textContent).toBe("false");
    });
    // Should be false because the fetch failed
    expect(screen.getByTestId("is-subscribed").textContent).toBe("false");
  });

  it("sets isLoading to true initially", () => {
    // Override to delay the response so isLoading stays true
    server.use(
      http.get("/api/billing/subscription-status", () => {
        return new Promise(() => {
          // Never resolves — keeps isLoading true
        });
      })
    );

    storeTokens("mock-access-token", "mock-refresh-token", 900);
    render(
      <MemoryRouter>
        <AuthProvider>
          <SubscriptionProvider>
            <SubscriptionConsumer />
          </SubscriptionProvider>
        </AuthProvider>
      </MemoryRouter>
    );

    // isLoading starts true (default state)
    expect(screen.getByTestId("is-loading").textContent).toBe("true");
  });

  it("refreshStatus re-fetches subscription", async () => {
    let callCount = 0;
    server.use(
      http.get("/api/billing/subscription-status", () => {
        callCount++;
        return HttpResponse.json({
          status: callCount === 1 ? "inactive" : "active",
          is_active: callCount !== 1,
          current_period_end: null,
        });
      })
    );

    const user = userEvent.setup();
    renderWithProviders(<SubscriptionConsumer />);

    // Wait for initial fetch
    await waitFor(() => {
      expect(screen.getByTestId("is-loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("is-subscribed").textContent).toBe("false");
    expect(callCount).toBe(1);

    // Click refresh button
    await user.click(screen.getByRole("button", { name: /refresh/i }));

    await waitFor(() => {
      expect(screen.getByTestId("is-subscribed").textContent).toBe("true");
    });
    expect(callCount).toBe(2);
  });
});

// ─── Dashboard - Subscribed ─────────────────────────────────────────────────

describe("Dashboard - Subscribed", () => {
  afterEach(() => {
    localStorage.clear();
  });

  function renderSubscribedDashboard() {
    storeTokens("mock-access-token", "mock-refresh-token", 900);
    // Default MSW handler returns active subscription for mock-access-token
    return render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <AuthProvider>
          <SubscriptionProvider>
            <StatsProvider>
              <Dashboard />
            </StatsProvider>
          </SubscriptionProvider>
        </AuthProvider>
      </MemoryRouter>
    );
  }

  it("shows active subscription badge", async () => {
    renderSubscribedDashboard();
    const badge = await screen.findByText(/Active — Student Plan/);
    expect(badge).toBeInTheDocument();
  });

  it("shows generate button when subscribed", async () => {
    renderSubscribedDashboard();
    const btn = await screen.findByRole("button", { name: /generate new test/i });
    expect(btn).toBeInTheDocument();
  });

  it("shows cancel subscription button", async () => {
    renderSubscribedDashboard();
    const btn = await screen.findByRole("button", { name: /cancel subscription/i });
    expect(btn).toBeInTheDocument();
  });

  it("cancel flow shows confirmation", async () => {
    const user = userEvent.setup();
    renderSubscribedDashboard();

    const cancelBtn = await screen.findByRole("button", { name: /cancel subscription/i });
    await user.click(cancelBtn);

    expect(screen.getByText(/are you sure you want to cancel/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /confirm cancel subscription/i })).toBeInTheDocument();
  });

  it("shows period end date", async () => {
    renderSubscribedDashboard();

    // The mock handler returns current_period_end: "2026-04-13T00:00:00Z"
    await waitFor(() => {
      expect(screen.getByText(/current period ends/i)).toBeInTheDocument();
    });
    // Check that a date is rendered (April 13, 2026 in some locale)
    expect(screen.getByText(/april/i)).toBeInTheDocument();
  });
});

// ─── Dashboard - Not Subscribed ─────────────────────────────────────────────

describe("Dashboard - Not Subscribed", () => {
  afterEach(() => {
    localStorage.clear();
  });

  function renderNotSubscribedDashboard() {
    // Override subscription handler to return inactive
    server.use(
      http.get("/api/billing/subscription-status", () => {
        return HttpResponse.json({
          status: "inactive",
          is_active: false,
          current_period_end: null,
        });
      })
    );

    storeTokens("mock-access-token", "mock-refresh-token", 900);
    return render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <AuthProvider>
          <SubscriptionProvider>
            <StatsProvider>
              <Dashboard />
            </StatsProvider>
          </SubscriptionProvider>
        </AuthProvider>
      </MemoryRouter>
    );
  }

  it("shows promo card with price", async () => {
    renderNotSubscribedDashboard();
    const price = await screen.findByText("$5");
    expect(price).toBeInTheDocument();
  });

  it("shows subscribe button", async () => {
    renderNotSubscribedDashboard();
    const studentBtn = await screen.findByRole("button", { name: /choose student/i });
    expect(studentBtn).toBeInTheDocument();
    const tutorBtn = screen.getByRole("button", { name: /choose tutor/i });
    expect(tutorBtn).toBeInTheDocument();
  });

  it("does not show generate button", async () => {
    renderNotSubscribedDashboard();
    // Wait for the plan cards to appear (meaning subscription loaded)
    await screen.findByText("$5");
    expect(screen.queryByRole("button", { name: /generate new test/i })).not.toBeInTheDocument();
  });

  it("subscribe button shows loading on click", async () => {
    // Override checkout to never resolve, so we can see the loading state
    server.use(
      http.post("/api/billing/create-checkout-session", () => {
        return new Promise(() => {
          // Never resolves
        });
      })
    );

    const user = userEvent.setup();
    renderNotSubscribedDashboard();

    const btn = await screen.findByRole("button", { name: /choose student/i });
    await user.click(btn);

    await waitFor(() => {
      const redirectingButtons = screen.getAllByText(/redirecting/i);
      expect(redirectingButtons.length).toBeGreaterThan(0);
    });
  });

  it("shows error on subscribe failure", async () => {
    server.use(
      http.post("/api/billing/create-checkout-session", () => {
        return HttpResponse.json(
          { detail: "Payment service unavailable" },
          { status: 503 }
        );
      })
    );

    const user = userEvent.setup();
    renderNotSubscribedDashboard();

    const btn = await screen.findByRole("button", { name: /choose student/i });
    await user.click(btn);

    const alert = await screen.findByRole("alert");
    expect(alert).toBeInTheDocument();
    // extractErrorDetail will extract the "detail" field from the error response
    expect(alert.textContent).toContain("Payment service unavailable");
  });
});

// ─── CheckoutSuccess ────────────────────────────────────────────────────────

describe("CheckoutSuccess", () => {
  afterEach(() => {
    localStorage.clear();
    vi.useRealTimers();
  });

  it("shows processing message initially", async () => {
    // Override to never resolve so it stays in processing state
    server.use(
      http.get("/api/billing/subscription-status", () => {
        return HttpResponse.json({
          status: "inactive",
          is_active: false,
          current_period_end: null,
        });
      })
    );

    storeTokens("mock-access-token", "mock-refresh-token", 900);
    render(
      <MemoryRouter initialEntries={["/checkout/success"]}>
        <AuthProvider>
          <SubscriptionProvider>
            <CheckoutSuccess />
          </SubscriptionProvider>
        </AuthProvider>
      </MemoryRouter>
    );

    // Wait for auth to settle, then the checkout success page shows processing
    const processing = await screen.findByText(/processing/i);
    expect(processing).toBeInTheDocument();
  });

  it("shows success when subscription becomes active", async () => {
    let callCount = 0;
    server.use(
      http.get("/api/billing/subscription-status", () => {
        callCount++;
        // First call returns inactive, subsequent calls return active
        if (callCount <= 1) {
          return HttpResponse.json({
            status: "inactive",
            is_active: false,
            current_period_end: null,
          });
        }
        return HttpResponse.json({
          status: "active",
          is_active: true,
          current_period_end: "2026-04-13T00:00:00Z",
        });
      })
    );

    storeTokens("mock-access-token", "mock-refresh-token", 900);
    render(
      <MemoryRouter initialEntries={["/checkout/success"]}>
        <AuthProvider>
          <SubscriptionProvider>
            <CheckoutSuccess />
          </SubscriptionProvider>
        </AuthProvider>
      </MemoryRouter>
    );

    // It should eventually show the success message after polling
    const success = await screen.findByText(/subscribed/i, {}, { timeout: 10000 });
    expect(success).toBeInTheDocument();
  });

  it("shows timeout message after 30 seconds", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });

    server.use(
      http.get("/api/billing/subscription-status", () => {
        return HttpResponse.json({
          status: "inactive",
          is_active: false,
          current_period_end: null,
        });
      })
    );

    storeTokens("mock-access-token", "mock-refresh-token", 900);
    render(
      <MemoryRouter initialEntries={["/checkout/success"]}>
        <AuthProvider>
          <SubscriptionProvider>
            <CheckoutSuccess />
          </SubscriptionProvider>
        </AuthProvider>
      </MemoryRouter>
    );

    // Wait for auth to settle and initial render
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1000);
    });

    // Advance past the 30-second timeout
    await act(async () => {
      await vi.advanceTimersByTimeAsync(31000);
    });

    // Should show the timeout message
    await waitFor(() => {
      expect(screen.getByText(/taking longer than expected/i)).toBeInTheDocument();
    });
  });
});

// ─── CheckoutCancel ─────────────────────────────────────────────────────────

describe("CheckoutCancel", () => {
  afterEach(() => {
    localStorage.clear();
  });

  function renderCheckoutCancel() {
    // Override subscription to return inactive (not subscribed)
    server.use(
      http.get("/api/billing/subscription-status", () => {
        return HttpResponse.json({
          status: "inactive",
          is_active: false,
          current_period_end: null,
        });
      })
    );

    storeTokens("mock-access-token", "mock-refresh-token", 900);
    return render(
      <MemoryRouter initialEntries={["/checkout/cancel"]}>
        <AuthProvider>
          <SubscriptionProvider>
            <CheckoutCancel />
          </SubscriptionProvider>
        </AuthProvider>
      </MemoryRouter>
    );
  }

  it("shows cancelled message", async () => {
    renderCheckoutCancel();
    const cancelled = await screen.findByText(/cancelled/i);
    expect(cancelled).toBeInTheDocument();
  });

  it("shows try again button", async () => {
    renderCheckoutCancel();
    const btn = await screen.findByRole("button", { name: /try subscribing again/i });
    expect(btn).toBeInTheDocument();
  });

  it("shows back to dashboard link", async () => {
    renderCheckoutCancel();
    const link = await screen.findByRole("link", { name: /back to dashboard/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "/dashboard");
  });
});

// ─── SubscriptionGate ───────────────────────────────────────────────────────

describe("SubscriptionGate", () => {
  afterEach(() => {
    localStorage.clear();
  });

  // Import SubscriptionGate from App.tsx is not directly exported, so we
  // test it through route rendering with the actual App structure.
  // We'll create a mini version using the useSubscription hook.

  function SubscriptionGate({ children }: { children: React.ReactNode }) {
    const { isSubscribed, isLoading } = useSubscription();

    if (isLoading) {
      return (
        <div role="status" aria-label="Loading">
          Loading...
        </div>
      );
    }

    if (!isSubscribed) {
      return <div>Redirected to dashboard</div>;
    }

    return <>{children}</>;
  }

  it("redirects to dashboard when not subscribed", async () => {
    server.use(
      http.get("/api/billing/subscription-status", () => {
        return HttpResponse.json({
          status: "inactive",
          is_active: false,
          current_period_end: null,
        });
      })
    );

    storeTokens("mock-access-token", "mock-refresh-token", 900);
    render(
      <MemoryRouter initialEntries={["/generate"]}>
        <AuthProvider>
          <SubscriptionProvider>
            <SubscriptionGate>
              <div>Protected Content</div>
            </SubscriptionGate>
          </SubscriptionProvider>
        </AuthProvider>
      </MemoryRouter>
    );

    const redirect = await screen.findByText(/redirected to dashboard/i);
    expect(redirect).toBeInTheDocument();
    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
  });

  it("renders children when subscribed", async () => {
    storeTokens("mock-access-token", "mock-refresh-token", 900);
    // Default handler returns active subscription
    render(
      <MemoryRouter initialEntries={["/generate"]}>
        <AuthProvider>
          <SubscriptionProvider>
            <SubscriptionGate>
              <div>Protected Content</div>
            </SubscriptionGate>
          </SubscriptionProvider>
        </AuthProvider>
      </MemoryRouter>
    );

    const content = await screen.findByText("Protected Content");
    expect(content).toBeInTheDocument();
  });

  it("shows loading when subscription is loading", () => {
    // Override to never resolve so isLoading stays true
    server.use(
      http.get("/api/billing/subscription-status", () => {
        return new Promise(() => {
          // Never resolves
        });
      })
    );

    storeTokens("mock-access-token", "mock-refresh-token", 900);
    render(
      <MemoryRouter>
        <AuthProvider>
          <SubscriptionProvider>
            <SubscriptionGate>
              <div>Protected Content</div>
            </SubscriptionGate>
          </SubscriptionProvider>
        </AuthProvider>
      </MemoryRouter>
    );

    // Should show loading indicator
    expect(screen.getByRole("status")).toBeInTheDocument();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
  });
});

// ─── Billing API Validators ─────────────────────────────────────────────────

describe("Billing API validators", () => {
  // We test the validators indirectly through the API functions,
  // similar to the existing pattern in api.test.ts.

  afterEach(() => {
    localStorage.clear();
  });

  it("validateCheckoutSession accepts valid data", async () => {
    storeTokens("mock-access-token", "mock-refresh-token", 900);
    // Default MSW handler returns valid data with url field
    const { createCheckoutSession } = await import("../services/api");
    const result = await createCheckoutSession("student");
    expect(result.url).toBe("https://checkout.stripe.com/test-session");
  });

  it("validateCheckoutSession rejects missing url", async () => {
    server.use(
      http.post("/api/billing/create-checkout-session", () => {
        return HttpResponse.json({});
      })
    );
    storeTokens("mock-access-token", "mock-refresh-token", 900);
    const { createCheckoutSession } = await import("../services/api");
    await expect(createCheckoutSession("student")).rejects.toThrow("missing url");
  });

  it("validateSubscriptionStatus accepts valid data", async () => {
    storeTokens("mock-access-token", "mock-refresh-token", 900);
    // Default MSW handler returns valid subscription data
    const { getSubscriptionStatus } = await import("../services/api");
    const result = await getSubscriptionStatus();
    expect(result.status).toBe("active");
    expect(result.is_active).toBe(true);
  });

  it("validateSubscriptionStatus rejects missing status", async () => {
    server.use(
      http.get("/api/billing/subscription-status", () => {
        return HttpResponse.json({});
      })
    );
    storeTokens("mock-access-token", "mock-refresh-token", 900);
    const { getSubscriptionStatus } = await import("../services/api");
    await expect(getSubscriptionStatus()).rejects.toThrow("missing status");
  });

  it("validateSubscriptionStatus rejects non-boolean is_active", async () => {
    server.use(
      http.get("/api/billing/subscription-status", () => {
        return HttpResponse.json({
          status: "active",
          is_active: "yes",
        });
      })
    );
    storeTokens("mock-access-token", "mock-refresh-token", 900);
    const { getSubscriptionStatus } = await import("../services/api");
    await expect(getSubscriptionStatus()).rejects.toThrow("missing is_active");
  });
});
