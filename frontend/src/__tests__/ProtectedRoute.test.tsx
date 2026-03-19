import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import ProtectedRoute from "../components/Auth/ProtectedRoute";
import { clearTokens, storeTokens } from "../services/api";

function renderProtected(hasTokens: boolean) {
  if (hasTokens) {
    storeTokens("mock-access-token", "mock-refresh-token", 900);
  } else {
    clearTokens();
  }

  return render(
    <MemoryRouter initialEntries={["/protected"]}>
      <AuthProvider>
        <Routes>
          <Route
            path="/protected"
            element={
              <ProtectedRoute>
                <div>Protected Content</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<div>Login Page</div>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("ProtectedRoute", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("shows loading initially when tokens exist", () => {
    renderProtected(true);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("renders children when authenticated", async () => {
    renderProtected(true);
    const content = await screen.findByText("Protected Content");
    expect(content).toBeInTheDocument();
  });

  it("redirects to login when not authenticated", async () => {
    renderProtected(false);
    const loginPage = await screen.findByText("Login Page");
    expect(loginPage).toBeInTheDocument();
  });
});
