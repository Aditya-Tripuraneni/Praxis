import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import Register from "../pages/Register";

function renderRegister() {
  return render(
    <MemoryRouter initialEntries={["/register"]}>
      <AuthProvider>
        <Register />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("Register", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("renders the registration form", () => {
    renderRegister();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    // The password label is "Password" (exact), and confirm is "Confirm Password"
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
  });

  it("shows minimum password length hint", () => {
    renderRegister();
    expect(screen.getByText(/minimum 8 characters/i)).toBeInTheDocument();
  });

  it("renders Create Account button", () => {
    renderRegister();
    expect(
      screen.getByRole("button", { name: /create account/i })
    ).toBeInTheDocument();
  });

  // Google OAuth disabled until consent screen is configured
  // it("renders Google OAuth button for signup", () => {
  //   renderRegister();
  //   expect(
  //     screen.getByRole("button", { name: /sign up with google/i })
  //   ).toBeInTheDocument();
  // });

  it("renders link to sign in page", () => {
    renderRegister();
    expect(screen.getByText(/sign in/i)).toBeInTheDocument();
  });

  it("shows success message after valid signup", async () => {
    const user = userEvent.setup();
    renderRegister();

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText("Password");
    const confirmInput = screen.getByLabelText(/confirm password/i);

    await user.clear(emailInput);
    await user.type(emailInput, "new@example.com");
    await user.clear(passwordInput);
    await user.type(passwordInput, "securepass123");
    await user.clear(confirmInput);
    await user.type(confirmInput, "securepass123");

    const submitBtn = screen.getByRole("button", { name: /create account/i });
    await user.click(submitBtn);

    const successHeading = await screen.findByRole("heading", { name: /check your email/i }, { timeout: 3000 });
    expect(successHeading).toBeInTheDocument();
  });

  it("shows password mismatch error when passwords differ", async () => {
    const user = userEvent.setup();
    renderRegister();

    await user.type(screen.getByLabelText(/email/i), "new@example.com");
    await user.type(screen.getByLabelText("Password"), "securepass123");
    await user.type(
      screen.getByLabelText(/confirm password/i),
      "differentpass"
    );
    await user.click(
      screen.getByRole("button", { name: /create account/i })
    );

    await waitFor(() => {
      expect(
        screen.getByText(/passwords do not match/i)
      ).toBeInTheDocument();
    });
  });
});
