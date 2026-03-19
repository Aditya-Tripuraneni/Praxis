import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import TopicSelector from "../components/TestConfig/TopicSelector";
import type { TopicInfo } from "../types";

// ---------------------------------------------------------------------------
// Test data
// ---------------------------------------------------------------------------

const mockTopics: TopicInfo[] = [
  {
    id: "algebra",
    name: "Algebra",
    subtopics: [
      { id: "linear_equations", name: "Linear Equations" },
      { id: "quadratic", name: "Quadratic Equations" },
      { id: "polynomials", name: "Polynomials" },
    ],
    difficulties: ["easy", "medium", "hard"],
    template_count: 9,
  },
  {
    id: "trigonometry",
    name: "Trigonometry",
    subtopics: [
      { id: "trig_evaluation", name: "Trig Evaluation" },
      { id: "trig_equation", name: "Trig Equations" },
    ],
    difficulties: ["easy", "medium", "hard"],
    template_count: 5,
  },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderSelector(selected: string[] = [], onChange = vi.fn()) {
  const user = userEvent.setup();
  return {
    user,
    onChange,
    ...render(
      <TopicSelector
        topics={mockTopics}
        selected={selected}
        onChange={onChange}
      />
    ),
  };
}

/** Return the header button (role="button") for a given topic name. */
function getTopicHeader(name: string) {
  // The topic name text appears in both a visually-hidden <legend> and a <span>
  // inside the role="button" header, so getByText returns multiple matches.
  // Instead, find all text matches and pick the one inside a role="button" ancestor.
  const matches = screen.getAllByText(name);
  for (const el of matches) {
    const button = el.closest('[role="button"]');
    if (button) return button as HTMLElement;
  }
  throw new Error(`Could not find topic header for "${name}"`);
}

/** Expand a topic by clicking its header. */
async function expandTopic(user: ReturnType<typeof userEvent.setup>, name: string) {
  const header = getTopicHeader(name);
  await user.click(header);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("TopicSelector", () => {
  // -----------------------------------------------------------------------
  // Rendering
  // -----------------------------------------------------------------------
  describe("rendering", () => {
    it("renders all topic names from provided data", () => {
      renderSelector();
      // Topic name appears in both a visually-hidden <legend> and the header <span>,
      // so we verify at least one match exists for each topic.
      expect(screen.getAllByText("Algebra").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("Trigonometry").length).toBeGreaterThanOrEqual(1);
    });

    it("renders the outer Topics legend", () => {
      renderSelector();
      expect(screen.getByText("Topics")).toBeInTheDocument();
    });

    it("renders template count badges for each topic", () => {
      renderSelector();
      expect(screen.getByText("9 templates")).toBeInTheDocument();
      expect(screen.getByText("5 templates")).toBeInTheDocument();
    });

    it("renders singular template text when count is 1", () => {
      const singleTopic: TopicInfo[] = [
        {
          id: "misc",
          name: "Misc",
          subtopics: [{ id: "a", name: "A" }],
          difficulties: ["easy"],
          template_count: 1,
        },
      ];
      render(
        <TopicSelector topics={singleTopic} selected={[]} onChange={vi.fn()} />
      );
      expect(screen.getByText("1 template")).toBeInTheDocument();
    });

    it("renders a topic-level checkbox for each topic with correct aria-label", () => {
      renderSelector();
      expect(
        screen.getByRole("checkbox", { name: /select all algebra subtopics/i })
      ).toBeInTheDocument();
      expect(
        screen.getByRole("checkbox", {
          name: /select all trigonometry subtopics/i,
        })
      ).toBeInTheDocument();
    });

    it("does not render subtopics when collapsed", () => {
      renderSelector();
      expect(screen.queryByText("Linear Equations")).not.toBeInTheDocument();
      expect(screen.queryByText("Trig Evaluation")).not.toBeInTheDocument();
    });

    it("renders subtopics when a topic is expanded", async () => {
      const { user } = renderSelector();
      await expandTopic(user, "Algebra");

      expect(screen.getByText("Linear Equations")).toBeInTheDocument();
      expect(screen.getByText("Quadratic Equations")).toBeInTheDocument();
      expect(screen.getByText("Polynomials")).toBeInTheDocument();
    });

    it("renders a subtopic group with correct aria-label when expanded", async () => {
      const { user } = renderSelector();
      await expandTopic(user, "Algebra");

      expect(
        screen.getByRole("group", { name: "Algebra subtopics" })
      ).toBeInTheDocument();
    });

    it("shows the selected count badge when some subtopics are selected", () => {
      renderSelector(["algebra.linear_equations"]);
      expect(screen.getByText(/1\/3 selected/)).toBeInTheDocument();
    });

    it("shows the selected count badge when all subtopics are selected", () => {
      renderSelector(["algebra"]);
      expect(screen.getByText(/3\/3 selected/)).toBeInTheDocument();
    });

    it("does not show a selected count badge when nothing is selected", () => {
      renderSelector();
      expect(screen.queryByText(/selected/)).not.toBeInTheDocument();
    });
  });

  // -----------------------------------------------------------------------
  // Expand / collapse
  // -----------------------------------------------------------------------
  describe("expand / collapse", () => {
    it("topics start collapsed (aria-expanded=false)", () => {
      renderSelector();
      const header = getTopicHeader("Algebra");
      expect(header).toHaveAttribute("aria-expanded", "false");
    });

    it("clicking topic header expands it (aria-expanded=true)", async () => {
      const { user } = renderSelector();
      const header = getTopicHeader("Algebra");
      await user.click(header);

      expect(header).toHaveAttribute("aria-expanded", "true");
    });

    it("clicking expanded topic header collapses it", async () => {
      const { user } = renderSelector();
      const header = getTopicHeader("Algebra");

      await user.click(header); // expand
      expect(header).toHaveAttribute("aria-expanded", "true");

      await user.click(header); // collapse
      expect(header).toHaveAttribute("aria-expanded", "false");
    });

    it("expanding one topic does not affect another", async () => {
      const { user } = renderSelector();
      await expandTopic(user, "Algebra");

      const trigHeader = getTopicHeader("Trigonometry");
      expect(trigHeader).toHaveAttribute("aria-expanded", "false");
    });

    it("clicking the topic checkbox does not toggle expand/collapse", async () => {
      const { user } = renderSelector();
      const header = getTopicHeader("Algebra");
      const checkbox = screen.getByRole("checkbox", {
        name: /select all algebra subtopics/i,
      });

      await user.click(checkbox);
      // Header should still be collapsed because stopPropagation prevents it
      expect(header).toHaveAttribute("aria-expanded", "false");
    });
  });

  // -----------------------------------------------------------------------
  // Keyboard navigation
  // -----------------------------------------------------------------------
  describe("keyboard navigation", () => {
    it("Enter key on topic header toggles expand", async () => {
      const { user } = renderSelector();
      const header = getTopicHeader("Algebra");
      header.focus();

      await user.keyboard("{Enter}");
      expect(header).toHaveAttribute("aria-expanded", "true");

      await user.keyboard("{Enter}");
      expect(header).toHaveAttribute("aria-expanded", "false");
    });

    it("Space key on topic header toggles expand", async () => {
      const { user } = renderSelector();
      const header = getTopicHeader("Algebra");
      header.focus();

      await user.keyboard(" ");
      expect(header).toHaveAttribute("aria-expanded", "true");

      await user.keyboard(" ");
      expect(header).toHaveAttribute("aria-expanded", "false");
    });
  });

  // -----------------------------------------------------------------------
  // Topic-level checkbox (select all / deselect all)
  // -----------------------------------------------------------------------
  describe("topic checkbox — select all / deselect all", () => {
    it("clicking topic checkbox when none selected calls onChange with all subtopics (bare topic name)", async () => {
      const { user, onChange } = renderSelector();

      const checkbox = screen.getByRole("checkbox", {
        name: /select all algebra subtopics/i,
      });
      await user.click(checkbox);

      // When all subtopics are selected, serialization yields the bare topic name
      expect(onChange).toHaveBeenCalledTimes(1);
      expect(onChange).toHaveBeenCalledWith(["algebra"]);
    });

    it("clicking topic checkbox when all selected calls onChange with empty array", async () => {
      const { user, onChange } = renderSelector(["algebra"]);

      const checkbox = screen.getByRole("checkbox", {
        name: /select all algebra subtopics/i,
      });
      await user.click(checkbox);

      expect(onChange).toHaveBeenCalledTimes(1);
      expect(onChange).toHaveBeenCalledWith([]);
    });

    it("clicking topic checkbox when some selected calls onChange with all subtopics (select all)", async () => {
      const { user, onChange } = renderSelector(["algebra.linear_equations"]);

      const checkbox = screen.getByRole("checkbox", {
        name: /select all algebra subtopics/i,
      });
      await user.click(checkbox);

      expect(onChange).toHaveBeenCalledTimes(1);
      expect(onChange).toHaveBeenCalledWith(["algebra"]);
    });

    it("selecting one topic does not affect another topic's selection", async () => {
      const { user, onChange } = renderSelector(["trigonometry"]);

      const algebraCheckbox = screen.getByRole("checkbox", {
        name: /select all algebra subtopics/i,
      });
      await user.click(algebraCheckbox);

      expect(onChange).toHaveBeenCalledTimes(1);
      const result = onChange.mock.calls[0][0] as string[];
      expect(result).toContain("algebra");
      expect(result).toContain("trigonometry");
    });
  });

  // -----------------------------------------------------------------------
  // Topic checkbox states (checked / unchecked / indeterminate)
  // -----------------------------------------------------------------------
  describe("topic checkbox states", () => {
    it("is unchecked when no subtopics are selected", () => {
      renderSelector();
      const checkbox = screen.getByRole("checkbox", {
        name: /select all algebra subtopics/i,
      }) as HTMLInputElement;

      expect(checkbox.checked).toBe(false);
      expect(checkbox.indeterminate).toBe(false);
    });

    it("is checked when all subtopics are selected (bare topic name)", () => {
      renderSelector(["algebra"]);
      const checkbox = screen.getByRole("checkbox", {
        name: /select all algebra subtopics/i,
      }) as HTMLInputElement;

      expect(checkbox.checked).toBe(true);
      expect(checkbox.indeterminate).toBe(false);
    });

    it("is checked when all subtopics are selected (explicit dot-notation)", () => {
      renderSelector([
        "algebra.linear_equations",
        "algebra.quadratic",
        "algebra.polynomials",
      ]);
      const checkbox = screen.getByRole("checkbox", {
        name: /select all algebra subtopics/i,
      }) as HTMLInputElement;

      expect(checkbox.checked).toBe(true);
      expect(checkbox.indeterminate).toBe(false);
    });

    it("is indeterminate when some but not all subtopics are selected", () => {
      renderSelector(["algebra.linear_equations"]);
      const checkbox = screen.getByRole("checkbox", {
        name: /select all algebra subtopics/i,
      }) as HTMLInputElement;

      expect(checkbox.checked).toBe(false);
      expect(checkbox.indeterminate).toBe(true);
    });

    it("is indeterminate when two of three subtopics are selected", () => {
      renderSelector(["algebra.linear_equations", "algebra.quadratic"]);
      const checkbox = screen.getByRole("checkbox", {
        name: /select all algebra subtopics/i,
      }) as HTMLInputElement;

      expect(checkbox.checked).toBe(false);
      expect(checkbox.indeterminate).toBe(true);
    });
  });

  // -----------------------------------------------------------------------
  // Subtopic selection
  // -----------------------------------------------------------------------
  describe("subtopic selection", () => {
    it("clicking a subtopic checkbox toggles its selection on", async () => {
      const { user, onChange } = renderSelector();
      await expandTopic(user, "Algebra");

      const subtopicCheckbox = screen.getByRole("checkbox", {
        name: "Linear Equations",
      });
      await user.click(subtopicCheckbox);

      expect(onChange).toHaveBeenCalledTimes(1);
      expect(onChange).toHaveBeenCalledWith(["algebra.linear_equations"]);
    });

    it("clicking a selected subtopic checkbox removes it from selection", async () => {
      const { user, onChange } = renderSelector(["algebra.linear_equations"]);
      await expandTopic(user, "Algebra");

      const subtopicCheckbox = screen.getByRole("checkbox", {
        name: "Linear Equations",
      });
      await user.click(subtopicCheckbox);

      expect(onChange).toHaveBeenCalledTimes(1);
      expect(onChange).toHaveBeenCalledWith([]);
    });

    it("selecting the last remaining subtopic produces the bare topic name", async () => {
      const { user, onChange } = renderSelector([
        "algebra.linear_equations",
        "algebra.quadratic",
      ]);
      await expandTopic(user, "Algebra");

      const polynomialsCheckbox = screen.getByRole("checkbox", {
        name: "Polynomials",
      });
      await user.click(polynomialsCheckbox);

      expect(onChange).toHaveBeenCalledTimes(1);
      // All 3 subtopics now selected -> bare topic name
      expect(onChange).toHaveBeenCalledWith(["algebra"]);
    });

    it("deselecting one subtopic from full selection produces dot-notation for the rest", async () => {
      const { user, onChange } = renderSelector(["algebra"]);
      await expandTopic(user, "Algebra");

      const polynomialsCheckbox = screen.getByRole("checkbox", {
        name: "Polynomials",
      });
      await user.click(polynomialsCheckbox);

      expect(onChange).toHaveBeenCalledTimes(1);
      const result = onChange.mock.calls[0][0] as string[];
      expect(result).toHaveLength(2);
      expect(result).toContain("algebra.linear_equations");
      expect(result).toContain("algebra.quadratic");
      expect(result).not.toContain("algebra.polynomials");
    });

    it("subtopic checkboxes reflect selected state from props", async () => {
      const { user } = renderSelector([
        "algebra.linear_equations",
        "algebra.polynomials",
      ]);
      await expandTopic(user, "Algebra");

      const linearCheckbox = screen.getByRole("checkbox", {
        name: "Linear Equations",
      }) as HTMLInputElement;
      const quadraticCheckbox = screen.getByRole("checkbox", {
        name: "Quadratic Equations",
      }) as HTMLInputElement;
      const polynomialsCheckbox = screen.getByRole("checkbox", {
        name: "Polynomials",
      }) as HTMLInputElement;

      expect(linearCheckbox.checked).toBe(true);
      expect(quadraticCheckbox.checked).toBe(false);
      expect(polynomialsCheckbox.checked).toBe(true);
    });

    it("subtopic selection across multiple topics is independent", async () => {
      const { user, onChange } = renderSelector(["algebra.linear_equations"]);
      await expandTopic(user, "Trigonometry");

      const trigEvalCheckbox = screen.getByRole("checkbox", {
        name: "Trig Evaluation",
      });
      await user.click(trigEvalCheckbox);

      expect(onChange).toHaveBeenCalledTimes(1);
      const result = onChange.mock.calls[0][0] as string[];
      expect(result).toContain("algebra.linear_equations");
      expect(result).toContain("trigonometry.trig_evaluation");
    });
  });

  // -----------------------------------------------------------------------
  // Dot-notation serialization / parsing edge cases
  // -----------------------------------------------------------------------
  describe("dot-notation serialization", () => {
    it("bare topic name in selected prop is parsed as all subtopics selected", async () => {
      const { user } = renderSelector(["algebra"]);
      await expandTopic(user, "Algebra");

      const linearCheckbox = screen.getByRole("checkbox", {
        name: "Linear Equations",
      }) as HTMLInputElement;
      const quadraticCheckbox = screen.getByRole("checkbox", {
        name: "Quadratic Equations",
      }) as HTMLInputElement;
      const polynomialsCheckbox = screen.getByRole("checkbox", {
        name: "Polynomials",
      }) as HTMLInputElement;

      expect(linearCheckbox.checked).toBe(true);
      expect(quadraticCheckbox.checked).toBe(true);
      expect(polynomialsCheckbox.checked).toBe(true);
    });

    it("mixed bare and dot-notation selections are handled correctly", async () => {
      const { user, onChange } = renderSelector([
        "algebra",
        "trigonometry.trig_evaluation",
      ]);

      // Algebra: all selected (topic checkbox checked)
      const algebraCheckbox = screen.getByRole("checkbox", {
        name: /select all algebra subtopics/i,
      }) as HTMLInputElement;
      expect(algebraCheckbox.checked).toBe(true);
      expect(algebraCheckbox.indeterminate).toBe(false);

      // Trigonometry: partial (topic checkbox indeterminate)
      const trigCheckbox = screen.getByRole("checkbox", {
        name: /select all trigonometry subtopics/i,
      }) as HTMLInputElement;
      expect(trigCheckbox.checked).toBe(false);
      expect(trigCheckbox.indeterminate).toBe(true);

      // Deselect all algebra -> only trig remains
      await user.click(algebraCheckbox);

      expect(onChange).toHaveBeenCalledTimes(1);
      expect(onChange).toHaveBeenCalledWith(["trigonometry.trig_evaluation"]);
    });

    it("unknown topic ids in selected prop are silently ignored", () => {
      renderSelector(["nonexistent_topic", "algebra.linear_equations"]);

      // The component should still render without errors
      expect(screen.getAllByText("Algebra").length).toBeGreaterThanOrEqual(1);

      // Only algebra.linear_equations should count
      expect(screen.getByText(/1\/3 selected/)).toBeInTheDocument();
    });
  });

  // -----------------------------------------------------------------------
  // Empty / edge cases
  // -----------------------------------------------------------------------
  describe("edge cases", () => {
    it("renders without crashing when topics array is empty", () => {
      render(
        <TopicSelector topics={[]} selected={[]} onChange={vi.fn()} />
      );
      expect(screen.getByText("Topics")).toBeInTheDocument();
    });

    it("onChange is not called on initial render", () => {
      const onChange = vi.fn();
      renderSelector([], onChange);
      expect(onChange).not.toHaveBeenCalled();
    });

    it("handles both topics fully selected simultaneously", async () => {
      const { user, onChange } = renderSelector(["algebra", "trigonometry"]);

      // Deselect algebra
      const algebraCheckbox = screen.getByRole("checkbox", {
        name: /select all algebra subtopics/i,
      });
      await user.click(algebraCheckbox);

      expect(onChange).toHaveBeenCalledTimes(1);
      expect(onChange).toHaveBeenCalledWith(["trigonometry"]);
    });

    it("multiple subtopic toggles within same topic accumulate correctly", async () => {
      // Start with one subtopic selected, add another
      const { user, onChange } = renderSelector(["algebra.linear_equations"]);
      await expandTopic(user, "Algebra");

      const quadraticCheckbox = screen.getByRole("checkbox", {
        name: "Quadratic Equations",
      });
      await user.click(quadraticCheckbox);

      expect(onChange).toHaveBeenCalledTimes(1);
      const result = onChange.mock.calls[0][0] as string[];
      expect(result).toHaveLength(2);
      expect(result).toContain("algebra.linear_equations");
      expect(result).toContain("algebra.quadratic");
    });
  });
});
