import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import Generate from "../pages/Generate";
import { storeTokens } from "../services/api";

function renderGenerate() {
  storeTokens("mock-access-token", "mock-refresh-token", 900);
  return render(
    <MemoryRouter initialEntries={["/generate"]}>
      <AuthProvider>
        <Generate />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("Generate", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("shows loading state initially", () => {
    renderGenerate();
    expect(screen.getByText(/loading topics/i)).toBeInTheDocument();
  });

  it("renders the page heading after loading", async () => {
    renderGenerate();
    const heading = await screen.findByText(/configure your test/i);
    expect(heading).toBeInTheDocument();
  });

  it("renders topic selector with Algebra topic", async () => {
    renderGenerate();
    // Wait for topics API to resolve — "Algebra" comes from MSW handler
    await waitFor(() => {
      expect(screen.getAllByText("Algebra")[0]).toBeInTheDocument();
    });
  });

  it("renders the Topics legend", async () => {
    renderGenerate();
    const legend = await screen.findByText("Topics");
    expect(legend).toBeInTheDocument();
  });

  it("renders difficulty selector with Easy, Medium, Hard options", async () => {
    renderGenerate();
    await screen.findByText(/configure your test/i);
    expect(screen.getByLabelText(/easy/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/medium/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/hard/i)).toBeInTheDocument();
  });

  it("has Medium selected as default difficulty", async () => {
    renderGenerate();
    await screen.findByText(/configure your test/i);
    const mediumRadio = screen.getByLabelText(/medium/i);
    expect(mediumRadio).toBeChecked();
  });

  it("renders question count input with default value of 20", async () => {
    renderGenerate();
    await screen.findByText(/configure your test/i);
    const input = screen.getByLabelText(/number of questions/i);
    expect(input).toBeInTheDocument();
    expect(input).toHaveValue(20);
  });

  it("renders the Generate Test button", async () => {
    renderGenerate();
    await screen.findByText(/configure your test/i);
    expect(
      screen.getByRole("button", { name: /generate test/i })
    ).toBeInTheDocument();
  });

  it("has the generate button disabled when no topics selected", async () => {
    renderGenerate();
    await screen.findByText(/configure your test/i);
    const btn = screen.getByRole("button", { name: /generate test/i });
    expect(btn).toBeDisabled();
  });

  it("keeps generate disabled when count is 0", async () => {
    renderGenerate();
    await screen.findByText(/configure your test/i);

    // Select a topic first so only count validation controls button state
    const user = userEvent.setup();
    const algebraHeader = screen.getAllByText("Algebra")[0];
    await user.click(algebraHeader);

    const linearEqCheckbox = await screen.findByLabelText(
      /select all algebra subtopics/i
    );
    await user.click(linearEqCheckbox);

    // Count 0 is invalid under the new 1-50 range
    const countInput = screen.getByLabelText(/number of questions/i);
    await user.clear(countInput);
    await user.type(countInput, "0");

    const btn = screen.getByRole("button", { name: /generate test/i });
    expect(btn).toBeDisabled();
  });

  it("enables generate when count is 1 and a topic is selected", async () => {
    renderGenerate();
    await screen.findByText(/configure your test/i);

    const user = userEvent.setup();
    const algebraHeader = screen.getAllByText("Algebra")[0];
    await user.click(algebraHeader);

    const selectAllCheckbox = await screen.findByLabelText(
      /select all algebra subtopics/i
    );
    await user.click(selectAllCheckbox);

    const countInput = screen.getByLabelText(/number of questions/i);
    await user.clear(countInput);
    await user.type(countInput, "1");

    const btn = screen.getByRole("button", { name: /generate test/i });
    expect(btn).toBeEnabled();
  });

  it("allows changing difficulty via radio buttons", async () => {
    renderGenerate();
    await screen.findByText(/configure your test/i);
    const user = userEvent.setup();

    const easyRadio = screen.getByLabelText(/easy/i);
    await user.click(easyRadio);
    expect(easyRadio).toBeChecked();

    const hardRadio = screen.getByLabelText(/hard/i);
    await user.click(hardRadio);
    expect(hardRadio).toBeChecked();
  });

  it("allows changing the question count", async () => {
    renderGenerate();
    await screen.findByText(/configure your test/i);
    const user = userEvent.setup();

    const input = screen.getByLabelText(
      /number of questions/i
    ) as HTMLInputElement;
    await user.tripleClick(input);
    await user.keyboard("30");
    expect(input).toHaveValue(30);
  });

  it("enables generate button when a topic is selected and count is valid", async () => {
    renderGenerate();
    await screen.findByText(/configure your test/i);
    const user = userEvent.setup();

    // Expand Algebra and select all subtopics
    const algebraHeader = screen.getAllByText("Algebra")[0];
    await user.click(algebraHeader);
    const selectAllCheckbox = await screen.findByLabelText(
      /select all algebra subtopics/i
    );
    await user.click(selectAllCheckbox);

    const btn = screen.getByRole("button", { name: /generate test/i });
    expect(btn).toBeEnabled();
  });

  it("shows generating state when generate is clicked", async () => {
    renderGenerate();
    await screen.findByText(/configure your test/i);
    const user = userEvent.setup();

    // Select a topic
    const algebraHeader = screen.getAllByText("Algebra")[0];
    await user.click(algebraHeader);
    const selectAllCheckbox = await screen.findByLabelText(
      /select all algebra subtopics/i
    );
    await user.click(selectAllCheckbox);

    // Click generate
    const btn = screen.getByRole("button", { name: /generate test/i });
    await user.click(btn);

    // The button text should change to "Generating..."
    await waitFor(() => {
      expect(screen.getByText(/generating\.\.\./i)).toBeInTheDocument();
    });
  });
});
