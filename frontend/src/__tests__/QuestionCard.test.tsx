import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import QuestionCard from "../components/TestPreview/QuestionCard";
import type { QuestionResponse } from "../types";

const questionWithSteps: QuestionResponse = {
  id: 1,
  question_latex: "Solve for $x$: $3x + 5 = 14$",
  answer_latex: "$x = 3$",
  topic: "algebra",
  difficulty: "easy",
  subtopic: "linear_equations",
  solution_steps: ["$3x + 5 = 14$", "$3x = 9$", "$x = 3$"],
};

const questionWithoutSteps: QuestionResponse = {
  id: 2,
  question_latex: "Evaluate $\\sin(\\pi/6)$",
  answer_latex: "$\\frac{1}{2}$",
  topic: "trigonometry",
  difficulty: "easy",
  subtopic: "trig_evaluation",
  solution_steps: [],
};

describe("QuestionCard", () => {
  it("shows Show Solution button when steps exist", () => {
    render(<QuestionCard question={questionWithSteps} number={1} />);
    expect(
      screen.getByRole("button", { name: /show solution/i })
    ).toBeInTheDocument();
  });

  it("hides Show Solution button when no steps", () => {
    render(<QuestionCard question={questionWithoutSteps} number={1} />);
    expect(
      screen.queryByRole("button", { name: /show solution/i })
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /show answer/i })
    ).toBeInTheDocument();
  });

  it("clicking Show Solution reveals steps", async () => {
    render(<QuestionCard question={questionWithSteps} number={1} />);
    const user = userEvent.setup();

    await user.click(screen.getByRole("button", { name: /show solution/i }));

    expect(screen.getByText("Solution")).toBeInTheDocument();
    expect(
      screen.getByRole("region", { name: /worked solution/i })
    ).toBeInTheDocument();
  });

  it("Show Answer button hidden when solution is visible", async () => {
    render(<QuestionCard question={questionWithSteps} number={1} />);
    const user = userEvent.setup();

    await user.click(screen.getByRole("button", { name: /show solution/i }));

    expect(
      screen.queryByRole("button", { name: /show answer/i })
    ).not.toBeInTheDocument();
  });

  it("clicking Hide Solution restores Show Answer", async () => {
    render(<QuestionCard question={questionWithSteps} number={1} />);
    const user = userEvent.setup();

    await user.click(screen.getByRole("button", { name: /show solution/i }));
    expect(
      screen.queryByRole("button", { name: /show answer/i })
    ).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /hide solution/i }));
    expect(
      screen.getByRole("button", { name: /show answer/i })
    ).toBeInTheDocument();
  });

  it("Show Answer works independently when no steps", async () => {
    render(<QuestionCard question={questionWithoutSteps} number={1} />);
    const user = userEvent.setup();

    await user.click(screen.getByRole("button", { name: /show answer/i }));
    expect(screen.getByText("Answer")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /hide answer/i }));
    expect(screen.queryByText("Answer")).not.toBeInTheDocument();
  });
});
