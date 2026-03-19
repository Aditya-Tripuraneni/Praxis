import { http, HttpResponse } from "msw";

export const handlers = [
  // Existing topics handler
  http.get("/api/tests/topics", () => {
    return HttpResponse.json([
      {
        id: "algebra",
        name: "Algebra",
        subtopics: [{ id: "linear_equations", name: "Linear Equations" }],
        difficulties: ["easy", "medium", "hard"],
        template_count: 5,
      },
    ]);
  }),

  // Auth handlers
  http.post("/api/auth/login", async ({ request }) => {
    const body = (await request.json()) as { email: string; password: string };
    if (body.email === "test@example.com" && body.password === "validpass123") {
      return HttpResponse.json({
        access_token: "mock-access-token",
        refresh_token: "mock-refresh-token",
        expires_in: 900,
        token_type: "bearer",
        user: {
          id: "user-1",
          email: "test@example.com",
          email_verified: true,
          created_at: null,
        },
      });
    }
    return HttpResponse.json(
      { detail: "Invalid email or password" },
      { status: 401 }
    );
  }),

  http.post("/api/auth/signup", () => {
    return HttpResponse.json(
      {
        message:
          "Account created. Please check your email to verify your account.",
      },
      { status: 201 }
    );
  }),

  http.get("/api/auth/me", ({ request }) => {
    const auth = request.headers.get("Authorization");
    if (auth === "Bearer mock-access-token") {
      return HttpResponse.json({
        id: "user-1",
        email: "test@example.com",
        email_verified: true,
        created_at: null,
      });
    }
    return HttpResponse.json(
      { detail: "Not authenticated" },
      { status: 401 }
    );
  }),

  http.post("/api/auth/logout", () => {
    return HttpResponse.json({ message: "Logged out successfully" });
  }),

  http.delete("/api/auth/account", () => {
    return HttpResponse.json({ message: "Account deleted successfully" });
  }),

  http.post("/api/auth/resend-verification", () => {
    return HttpResponse.json({
      message:
        "If an account exists with this email, a verification link has been sent.",
    });
  }),

  http.post("/api/auth/verify-email", async ({ request }) => {
    const body = (await request.json()) as { email: string; token: string };
    if (body.token === "123456") {
      return HttpResponse.json({
        access_token: "verified-access-token",
        refresh_token: "verified-refresh-token",
        expires_in: 900,
        token_type: "bearer",
        user: {
          id: "user-1",
          email: body.email,
          email_verified: true,
          created_at: null,
        },
      });
    }
    return HttpResponse.json(
      { detail: "Invalid or expired verification code" },
      { status: 400 }
    );
  }),

  http.post("/api/auth/refresh", () => {
    return HttpResponse.json(
      { detail: "Invalid refresh token" },
      { status: 401 }
    );
  }),

  // Test generation
  http.post("/api/tests/generate", () => {
    return HttpResponse.json({
      test_id: "test-123",
      questions: [
        {
          id: 1,
          question_latex: "Solve $x + 1 = 2$",
          answer_latex: "$x = 1$",
          topic: "algebra",
          difficulty: "easy",
          subtopic: "linear_equations",
          solution_steps: ["$x + 1 = 2$", "$x = 2 - 1$", "$x = 1$"],
        },
        {
          id: 2,
          question_latex: "Solve $2x = 6$",
          answer_latex: "$x = 3$",
          topic: "algebra",
          difficulty: "easy",
          subtopic: "linear_equations",
          solution_steps: [],
        },
      ],
      created_at: "2026-03-12T00:00:00Z",
      config: {
        topics: ["algebra"],
        difficulty: "easy",
        count: 2,
      },
    });
  }),

  // Test retrieval
  http.get("/api/tests/:testId", ({ params }) => {
    if (params.testId === "test-123") {
      return HttpResponse.json({
        test_id: "test-123",
        questions: [
          {
            id: 1,
            question_latex: "Solve $x + 1 = 2$",
            answer_latex: "$x = 1$",
            topic: "algebra",
            difficulty: "easy",
            subtopic: "linear_equations",
            solution_steps: ["$x + 1 = 2$", "$x = 2 - 1$", "$x = 1$"],
          },
        ],
        created_at: "2026-03-12T00:00:00Z",
        config: {
          topics: ["algebra"],
          difficulty: "easy",
          count: 1,
        },
      });
    }
    return HttpResponse.json({ detail: "Test not found" }, { status: 404 });
  }),

  // PDF download
  http.get("/api/tests/:testId/pdf", ({ params }) => {
    if (params.testId === "test-123") {
      return new HttpResponse(new Blob(["fake-pdf-content"], { type: "application/pdf" }), {
        headers: { "Content-Type": "application/pdf" },
      });
    }
    return HttpResponse.json({ detail: "Test not found" }, { status: 404 });
  }),

  // Billing handlers
  http.get("/api/billing/subscription-status", ({ request }) => {
    const auth = request.headers.get("Authorization");
    if (auth === "Bearer mock-access-token") {
      return HttpResponse.json({
        status: "active",
        is_active: true,
        current_period_end: "2026-04-13T00:00:00Z",
        plan: "student",
      });
    }
    return HttpResponse.json(
      { detail: "Not authenticated" },
      { status: 401 }
    );
  }),

  http.post("/api/billing/create-checkout-session", ({ request }) => {
    const auth = request.headers.get("Authorization");
    if (auth === "Bearer mock-access-token") {
      return HttpResponse.json({
        url: "https://checkout.stripe.com/test-session",
      });
    }
    return HttpResponse.json(
      { detail: "Not authenticated" },
      { status: 401 }
    );
  }),

  http.post("/api/billing/cancel-subscription", ({ request }) => {
    const auth = request.headers.get("Authorization");
    if (auth === "Bearer mock-access-token") {
      return HttpResponse.json({
        message: "Subscription cancelled",
        cancel_at_period_end: true,
      });
    }
    return HttpResponse.json(
      { detail: "Not authenticated" },
      { status: 401 }
    );
  }),

  // Stats handler
  http.get("*/api/stats/me", () => {
    return HttpResponse.json({
      tests_generated: 18,
      questions_generated: 247,
      topic_counts: {
        algebra: 94,
        trigonometry: 62,
        calculus: 38,
        functions: 31,
        geometry: 22,
      },
      streak_current: 7,
      streak_best: 14,
      is_active_today: true,
    });
  }),
];
