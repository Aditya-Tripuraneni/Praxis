import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import AboutPraxis from "../pages/AboutPraxis";

describe("AboutPraxis", () => {
  it("renders hero content and KPI row", () => {
    render(
      <MemoryRouter>
        <AboutPraxis />
      </MemoryRouter>
    );

    expect(screen.getByText(/Generate fresh, exam-style math practice in seconds\./i)).toBeInTheDocument();
    expect(screen.getByText("Instant Preview")).toBeInTheDocument();
    expect(screen.getByText("Written Solutions")).toBeInTheDocument();
  });

  it("renders before and after comparison", () => {
    render(
      <MemoryRouter>
        <AboutPraxis />
      </MemoryRouter>
    );

    expect(screen.getByText("Before Praxis")).toBeInTheDocument();
    expect(screen.getByText("After Praxis")).toBeInTheDocument();
    expect(screen.getByText(/The same learner journey, redesigned by Praxis/i)).toBeInTheDocument();
  });

  it("renders FAQ accordion items", () => {
    const { container } = render(
      <MemoryRouter>
        <AboutPraxis />
      </MemoryRouter>
    );

    expect(screen.getByText("FAQ")).toBeInTheDocument();
    expect(screen.getByText(/Who uses Praxis\?/i)).toBeInTheDocument();
    expect(screen.getByText(/Do I need a separate AI chat subscription to use Praxis\?/i)).toBeInTheDocument();
    expect(container.querySelectorAll("details").length).toBeGreaterThanOrEqual(13);
  });
});
