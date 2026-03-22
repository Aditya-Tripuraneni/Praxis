import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { http, HttpResponse } from "msw";
import { server } from "../test/mocks/server";
import { AuthProvider } from "../context/AuthContext";
import { SubscriptionProvider } from "../context/SubscriptionContext";
import { StatsProvider } from "../context/StatsContext";
import Dashboard from "../pages/Dashboard";
import { storeTokens } from "../services/api";

function renderDashboard() {
  // Pre-set tokens so AuthContext thinks user is authenticated
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

describe("Dashboard", () => {
  beforeEach(() => {
    // Explicitly set subscription=active so this test is self-contained
    // and not affected by handler overrides in parallel test files.
    server.use(
      http.get("*/api/billing/subscription-status", () => {
        return HttpResponse.json({
          status: "active",
          is_active: true,
          current_period_end: "2026-04-13T00:00:00Z",
          plan: "student",
        });
      })
    );
  });

  afterEach(() => {
    localStorage.clear();
  });

  it("shows user email after loading", async () => {
    renderDashboard();
    // AuthContext calls /api/auth/me on mount — wait for it
    const email = await screen.findByText(/test@example\.com/i);
    expect(email).toBeInTheDocument();
  });

  it("shows welcome heading", async () => {
    renderDashboard();
    const heading = await screen.findByText(/welcome back/i);
    expect(heading).toBeInTheDocument();
  });

  it("has a generate test button when subscribed", async () => {
    renderDashboard();
    // Default MSW billing handler returns active subscription for mock-access-token.
    // Wait for both auth and subscription to settle.
    const btn = await screen.findByRole("button", {
      name: /generate new test/i,
    }, { timeout: 5000 });
    expect(btn).toBeInTheDocument();
  });

  it("has a sign out button", async () => {
    renderDashboard();
    const btn = await screen.findByRole("button", { name: /sign out/i });
    expect(btn).toBeInTheDocument();
  });

  it("has a delete account button", async () => {
    renderDashboard();
    const btn = await screen.findByRole("button", {
      name: /delete account/i,
    });
    expect(btn).toBeInTheDocument();
  });

  it("shows tests generated count from stats", async () => {
    renderDashboard();
    const count = await screen.findByText("18");
    expect(count).toBeInTheDocument();
  });

  it("shows questions practiced count from stats", async () => {
    renderDashboard();
    const count = await screen.findByText("247");
    expect(count).toBeInTheDocument();
  });

  it("shows streak count", async () => {
    renderDashboard();
    const streakNumber = await screen.findByText("7");
    expect(streakNumber).toBeInTheDocument();
    const streakLabel = await screen.findByText("day streak");
    expect(streakLabel).toBeInTheDocument();
  });

  it("shows best streak", async () => {
    renderDashboard();
    const best = await screen.findByText(/Best: 14 days/);
    expect(best).toBeInTheDocument();
  });

  it("shows topic mastery bars", async () => {
    renderDashboard();
    const algebra = await screen.findByText("Algebra");
    expect(algebra).toBeInTheDocument();
    expect(await screen.findByText("Trigonometry")).toBeInTheDocument();
    expect(await screen.findByText("Calculus")).toBeInTheDocument();
    expect(await screen.findByText("Functions")).toBeInTheDocument();
    expect(await screen.findByText("Geometry")).toBeInTheDocument();
  });

  it("shows start your streak when streak is 0", async () => {
    server.use(
      http.get("*/api/stats/me", () => {
        return HttpResponse.json({
          tests_generated: 0,
          questions_generated: 0,
          topic_counts: {},
          streak_current: 0,
          streak_best: 0,
          is_active_today: false,
        });
      })
    );
    renderDashboard();
    const msg = await screen.findByText(/Start your streak/);
    expect(msg).toBeInTheDocument();
  });

  it("shows placeholder when no questions generated", async () => {
    server.use(
      http.get("*/api/stats/me", () => {
        return HttpResponse.json({
          tests_generated: 0,
          questions_generated: 0,
          topic_counts: {},
          streak_current: 0,
          streak_best: 0,
          is_active_today: false,
        });
      })
    );
    renderDashboard();
    const msg = await screen.findByText(/Generate your first test/);
    expect(msg).toBeInTheDocument();
  });
});
