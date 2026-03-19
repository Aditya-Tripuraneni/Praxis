import { render, screen } from "@testing-library/react";
import MathRenderer from "../components/MathRenderer/MathRenderer";

describe("MathRenderer", () => {
  it("renders LaTeX expression with $ delimiters", () => {
    render(<MathRenderer latex="$x^2$" />);
    const katexEl = document.querySelector(".katex");
    expect(katexEl).toBeInTheDocument();
  });

  it("renders plain text without delimiters through KaTeX", () => {
    const { container } = render(<MathRenderer latex="hello world" />);
    // Without $ delimiters, the component still tries to render via KaTeX.
    // Verify the component renders without crashing and produces output.
    expect(container.querySelector("span")).toBeInTheDocument();
    expect(container.textContent).toContain("hello");
  });

  it("renders mixed text and math", () => {
    render(<MathRenderer latex="Solve $x + 1 = 2$" />);
    expect(screen.getByText(/Solve/)).toBeInTheDocument();
    expect(document.querySelector(".katex")).toBeInTheDocument();
  });
});
