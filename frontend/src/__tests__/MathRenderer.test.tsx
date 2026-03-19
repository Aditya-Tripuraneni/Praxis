import { render, screen } from "@testing-library/react";
import MathRenderer from "../components/MathRenderer/MathRenderer";

describe("MathRenderer", () => {
  it("renders LaTeX expression with $ delimiters", () => {
    render(<MathRenderer latex="$x^2$" />);
    const katexEl = document.querySelector(".katex");
    expect(katexEl).toBeInTheDocument();
  });

  it("renders plain text without delimiters as plain text", () => {
    const { container } = render(<MathRenderer latex="hello world" />);
    expect(container.querySelector("span")).toBeInTheDocument();
    expect(container.textContent).toContain("hello world");
    expect(document.querySelector(".katex")).not.toBeInTheDocument();
  });

  it("renders mixed text and math", () => {
    render(<MathRenderer latex="Solve $x + 1 = 2$" />);
    expect(screen.getByText(/Solve/)).toBeInTheDocument();
    expect(document.querySelector(".katex")).toBeInTheDocument();
  });
});
