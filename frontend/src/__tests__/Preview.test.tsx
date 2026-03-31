import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import { SubscriptionProvider } from "../context/SubscriptionContext";
import Preview from "../pages/Preview";
import { storeTokens } from "../services/api";
import { server } from "../test/mocks/server";

function renderPreview(testId: string = "test-123") {
  storeTokens("mock-access-token", "mock-refresh-token", 900);
  return render(
    <MemoryRouter initialEntries={[`/preview/${testId}`]}>
      <AuthProvider>
        <SubscriptionProvider>
          <Routes>
            <Route path="/preview/:testId" element={<Preview />} />
          </Routes>
        </SubscriptionProvider>
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("Preview", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("shows loading state initially", () => {
    renderPreview();
    expect(screen.getByText(/loading test/i)).toBeInTheDocument();
  });

  it("renders the page heading after loading", async () => {
    renderPreview();
    const heading = await screen.findByText(/test preview/i);
    expect(heading).toBeInTheDocument();
  });

  it("renders question cards after loading", async () => {
    renderPreview();
    // The MSW handler for test-123 returns 1 question; QuestionCard renders "Q1"
    const q1 = await screen.findByText("Q1");
    expect(q1).toBeInTheDocument();
  });

  it("renders Include topics in PDF footer checkbox", async () => {
    renderPreview();
    await screen.findByText(/test preview/i);
    const checkbox = screen.getByRole("checkbox", {
      name: /include topics in pdf footer/i,
    });
    expect(checkbox).toBeInTheDocument();
    expect(checkbox).not.toBeChecked();
  });

  it("renders difficulty metadata", async () => {
    renderPreview();
    await screen.findByText(/test preview/i);
    // config.difficulty is "easy" => displayed as "Difficulty: Easy"
    expect(screen.getByText(/difficulty: easy/i)).toBeInTheDocument();
  });

  it("renders question count metadata", async () => {
    renderPreview();
    await screen.findByText(/test preview/i);
    // test-123 has 1 question
    expect(screen.getByText(/1 question/i)).toBeInTheDocument();
  });

  it("renders the Download PDF button", async () => {
    renderPreview();
    await screen.findByText(/test preview/i);
    expect(
      screen.getByRole("button", { name: /download pdf/i })
    ).toBeInTheDocument();
  });

  it("renders the Include answers checkbox (checked by default)", async () => {
    renderPreview();
    await screen.findByText(/test preview/i);
    const checkbox = screen.getByRole("checkbox", { name: /include answers/i });
    expect(checkbox).toBeInTheDocument();
    expect(checkbox).toBeChecked();
  });

  it("renders the Generate New Test button", async () => {
    renderPreview();
    await screen.findByText(/test preview/i);
    expect(
      screen.getByRole("button", { name: /generate new test/i })
    ).toBeInTheDocument();
  });

  it("allows toggling the Include answers checkbox", async () => {
    renderPreview();
    await screen.findByText(/test preview/i);
    const user = userEvent.setup();

    const checkbox = screen.getByRole("checkbox", { name: /include answers/i });
    expect(checkbox).toBeChecked();

    await user.click(checkbox);
    expect(checkbox).not.toBeChecked();

    await user.click(checkbox);
    expect(checkbox).toBeChecked();
  });

  it("renders Show Answer toggle button on each question card", async () => {
    renderPreview();
    await screen.findByText("Q1");
    expect(
      screen.getByRole("button", { name: /show answer/i })
    ).toBeInTheDocument();
  });

  it("reveals answer when Show Answer is clicked", async () => {
    renderPreview();
    await screen.findByText("Q1");
    const user = userEvent.setup();

    const showBtn = screen.getByRole("button", { name: /show answer/i });
    await user.click(showBtn);

    // Button text changes to "Hide Answer"
    expect(
      screen.getByRole("button", { name: /hide answer/i })
    ).toBeInTheDocument();
  });

  it("hides answer when Hide Answer is clicked", async () => {
    renderPreview();
    await screen.findByText("Q1");
    const user = userEvent.setup();

    // Show answer first
    await user.click(screen.getByRole("button", { name: /show answer/i }));
    expect(
      screen.getByRole("button", { name: /hide answer/i })
    ).toBeInTheDocument();

    // Now hide it
    await user.click(screen.getByRole("button", { name: /hide answer/i }));
    expect(
      screen.getByRole("button", { name: /show answer/i })
    ).toBeInTheDocument();
  });

  it("shows error for nonexistent test", async () => {
    renderPreview("nonexistent-id");
    // The MSW handler returns 404 for unknown testId, which triggers the error state
    await waitFor(() => {
      expect(
        screen.getByText(/failed to load test/i)
      ).toBeInTheDocument();
    });
  });

  it("shows Generate New Test button on error state", async () => {
    renderPreview("nonexistent-id");
    await waitFor(() => {
      expect(screen.getByText(/failed to load test/i)).toBeInTheDocument();
    });
    expect(
      screen.getByRole("button", { name: /generate new test/i })
    ).toBeInTheDocument();
  });

  it("renders the questions list region", async () => {
    renderPreview();
    await screen.findByText("Q1");
    expect(
      screen.getByRole("region", { name: /questions list/i })
    ).toBeInTheDocument();
  });

  it("displays topic and difficulty tags on question card", async () => {
    renderPreview();
    await screen.findByText("Q1");
    // The QuestionCard renders topic and difficulty as tags
    expect(screen.getByText("Algebra")).toBeInTheDocument();
    expect(screen.getByText("Easy")).toBeInTheDocument();
    expect(screen.getByText("Linear Equations")).toBeInTheDocument();
  });

  it("shows Include solutions checkbox when questions have steps", async () => {
    renderPreview();
    await screen.findByText(/test preview/i);
    const checkbox = screen.getByRole("checkbox", {
      name: /include solutions/i,
    });
    expect(checkbox).toBeInTheDocument();
  });

  it("hides Include solutions checkbox when no questions have steps", async () => {
    server.use(
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
                solution_steps: [],
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
        return HttpResponse.json(
          { detail: "Test not found" },
          { status: 404 }
        );
      })
    );

    renderPreview();
    await screen.findByText(/test preview/i);
    expect(
      screen.queryByRole("checkbox", { name: /include solutions/i })
    ).not.toBeInTheDocument();
  });
});
