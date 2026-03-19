import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Landing from "../pages/Landing";

describe("Landing", () => {
  it("renders the title", () => {
    render(
      <MemoryRouter>
        <Landing />
      </MemoryRouter>
    );
    expect(screen.getAllByText("Praxis").length).toBeGreaterThan(0);
  });

  it("renders the Get Started button", () => {
    render(
      <MemoryRouter>
        <Landing />
      </MemoryRouter>
    );
    expect(screen.getAllByRole("button", { name: /get started/i }).length).toBeGreaterThan(0);
  });

  it("renders feature sections", () => {
    render(
      <MemoryRouter>
        <Landing />
      </MemoryRouter>
    );
    expect(screen.getByText("Topics")).toBeInTheDocument();
    expect(screen.getByText("Difficulty Levels")).toBeInTheDocument();
    expect(screen.getByText("Instant PDF")).toBeInTheDocument();
  });
});
