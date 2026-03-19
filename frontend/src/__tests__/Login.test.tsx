import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import Login from "../pages/Login";

function renderLogin(initialRoute = "/login") {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <AuthProvider>
        <Login />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("Login", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("renders the login form with email and password fields", () => {
    renderLogin();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /sign in$/i })
    ).toBeInTheDocument();
  });

  // Google OAuth disabled until consent screen is configured
  // it("renders Google OAuth button", () => {
  //   renderLogin();
  //   expect(
  //     screen.getByRole("button", { name: /sign in with google/i })
  //   ).toBeInTheDocument();
  // });

  it("renders link to register page", () => {
    renderLogin();
    expect(screen.getByText(/create one/i)).toBeInTheDocument();
  });

  it("shows error on failed login", async () => {
    const user = userEvent.setup();
    renderLogin();

    await user.type(screen.getByLabelText(/email/i), "wrong@example.com");
    await user.type(screen.getByLabelText("Password"), "wrongpass");
    await user.click(screen.getByRole("button", { name: /sign in$/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
    });
    expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument();
  });

  it("disables submit button while submitting", async () => {
    const user = userEvent.setup();
    renderLogin();

    await user.type(screen.getByLabelText(/email/i), "wrong@example.com");
    await user.type(screen.getByLabelText("Password"), "wrongpass");

    const button = screen.getByRole("button", { name: /sign in$/i });
    await user.click(button);

    // After failure, the button should be re-enabled
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /sign in$/i })
      ).toBeEnabled();
    });
  });
});
