import { useState, useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ChevronRight, Flame, Trophy, FileText, BookOpen, Search, Trash2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useSubscription } from "../context/SubscriptionContext";
import { useStats } from "../context/StatsContext";
import { extractErrorDetail, getSavedTests, deleteSavedTest } from "../services/api";
import type { SavedTestSummary } from "../types";

const bannerStyle: React.CSSProperties = {
  background: "linear-gradient(135deg, #134e4a 0%, #0d9488 100%)",
  padding: "var(--space-7) var(--space-7)",
  marginBottom: "var(--space-6)",
  marginTop: "calc(-1 * var(--space-8))",
};

const bannerHeadingStyle: React.CSSProperties = {
  fontSize: "1.75rem",
  fontWeight: 700,
  color: "#ffffff",
  marginBottom: "var(--space-2)",
};

const bannerEmailStyle: React.CSSProperties = {
  fontSize: "var(--font-size-base)",
  color: "#99f6e4",
};

const contentAreaStyle: React.CSSProperties = {
  maxWidth: "600px",
  margin: "0 auto",
  padding: "0 var(--space-4)",
};

const quickActionCardStyle: React.CSSProperties = {
  backgroundColor: "var(--bg-card)",
  boxShadow: "var(--shadow-card)",
  borderRadius: "var(--radius-md)",
  padding: "var(--space-6)",
  marginBottom: "var(--space-4)",
};

const subscriptionCardStyle: React.CSSProperties = {
  backgroundColor: "var(--bg-card)",
  boxShadow: "var(--shadow-card)",
  borderRadius: "var(--radius-md)",
  padding: "var(--space-5)",
  marginBottom: "var(--space-4)",
};

const statsRowStyle: React.CSSProperties = {
  display: "flex",
  gap: "var(--space-3)",
  marginBottom: "var(--space-4)",
};

const statCardStyle: React.CSSProperties = {
  flex: 1,
  textAlign: "center",
  padding: "var(--space-4)",
  boxShadow: "var(--shadow-card)",
  borderRadius: "var(--radius-md)",
  backgroundColor: "var(--bg-card)",
};

const accountCardStyle: React.CSSProperties = {
  backgroundColor: "var(--bg-card)",
  boxShadow: "var(--shadow-card)",
  borderRadius: "var(--radius-md)",
  padding: "var(--space-5)",
  marginBottom: "var(--space-4)",
};

const accountRowStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "var(--space-3) 0",
  width: "100%",
  background: "none",
  border: "none",
  cursor: "pointer",
  fontFamily: "var(--font-family)",
  fontSize: "var(--font-size-base)",
};

const sectionLabelStyle: React.CSSProperties = {
  textTransform: "uppercase",
  fontSize: "var(--font-size-xs)",
  fontWeight: 600,
  color: "var(--text-secondary)",
  marginBottom: "var(--space-3)",
  letterSpacing: "0.05em",
};

const streakCardStyle: React.CSSProperties = {
  backgroundColor: "var(--bg-card)",
  boxShadow: "var(--shadow-card)",
  borderRadius: "var(--radius-md)",
  padding: "var(--space-5)",
  marginBottom: "var(--space-4)",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
};

const streakLeftStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "var(--space-3)",
};

const streakNumberStyle: React.CSSProperties = {
  fontSize: "var(--font-size-2xl)",
  fontWeight: 800,
  color: "var(--color-primary-900)",
  lineHeight: 1,
};

const streakLabelStyle: React.CSSProperties = {
  fontSize: "var(--font-size-sm)",
  color: "var(--text-secondary)",
};

const bestStreakStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "var(--space-1)",
  fontSize: "var(--font-size-sm)",
  color: "var(--text-secondary)",
};

const dotsRowStyle: React.CSSProperties = {
  display: "flex",
  gap: "6px",
  marginTop: "var(--space-3)",
};

const masteryCardStyle: React.CSSProperties = {
  backgroundColor: "var(--bg-card)",
  boxShadow: "var(--shadow-card)",
  borderRadius: "var(--radius-md)",
  padding: "var(--space-5)",
  marginBottom: "var(--space-4)",
};

const topicRowStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "var(--space-3)",
  marginBottom: "var(--space-3)",
};

const barContainerStyle: React.CSSProperties = {
  flex: 1,
  height: 8,
  backgroundColor: "var(--color-stone-100)",
  borderRadius: "var(--radius-full)",
  overflow: "hidden",
};

const confirmBoxStyle: React.CSSProperties = {
  marginTop: "var(--space-3)",
  padding: "var(--space-4)",
  backgroundColor: "var(--color-error-bg)",
  borderRadius: "var(--radius-md)",
  border: "1px solid var(--color-error-border)",
};

const dangerBtnStyle: React.CSSProperties = {
  padding: "var(--space-2) var(--space-4)",
  fontSize: "var(--font-size-sm)",
  fontWeight: 500,
  fontFamily: "var(--font-family)",
  color: "var(--color-error-text)",
  backgroundColor: "var(--bg-card)",
  border: "1.5px solid var(--color-error-text)",
  borderRadius: "var(--radius-md)",
  cursor: "pointer",
  transition: "all var(--transition-fast)",
  minHeight: "44px",
};

const errorBoxStyle: React.CSSProperties = {
  color: "var(--color-error-text)",
  backgroundColor: "var(--color-error-bg)",
  border: "1px solid var(--color-error-border)",
  borderRadius: "var(--radius-md)",
  padding: "var(--space-3) var(--space-4)",
  marginBottom: "var(--space-4)",
  fontSize: "var(--font-size-sm)",
};

const TOPIC_COLORS: Record<string, { bar: string; text: string }> = {
  algebra: { bar: "var(--color-topic-algebra)", text: "var(--color-topic-algebra-text)" },
  functions: { bar: "var(--color-topic-functions)", text: "var(--color-topic-functions-text)" },
  geometry: { bar: "var(--color-topic-geometry)", text: "var(--color-topic-geometry-text)" },
  trigonometry: { bar: "var(--color-topic-trigonometry)", text: "var(--color-topic-trigonometry-text)" },
  calculus: { bar: "var(--color-topic-calculus)", text: "var(--color-topic-calculus-text)" },
};

export default function Dashboard() {
  const { user, logout, deleteAccount } = useAuth();
  const { subscription, isSubscribed, isLoading: subLoading, subscribe, cancelSub, plan, isTutor } = useSubscription();
  const { stats, isLoading: statsLoading } = useStats();
  const navigate = useNavigate();

  const [showConfirm, setShowConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);
  const [subError, setSubError] = useState("");
  const [isSubscribing, setIsSubscribing] = useState(false);
  const [savedTests, setSavedTests] = useState<SavedTestSummary[]>([]);
  const [savedTestsLoading, setSavedTestsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const handleLogout = useCallback(async () => {
    await logout();
    navigate("/", { replace: true });
  }, [logout, navigate]);

  const handleDeleteAccount = useCallback(async () => {
    setIsDeleting(true);
    try {
      await deleteAccount();
      navigate("/", { replace: true });
    } catch {
      setIsDeleting(false);
    }
  }, [deleteAccount, navigate]);

  const handleSubscribe = useCallback(async (selectedPlan: "student" | "tutor" = "student") => {
    setSubError("");
    setIsSubscribing(true);
    try {
      await subscribe(selectedPlan);
    } catch (err) {
      setSubError(extractErrorDetail(err, "Failed to start checkout. Please try again."));
      setIsSubscribing(false);
    }
  }, [subscribe]);

  const handleCancelSub = useCallback(async () => {
    setIsCancelling(true);
    setSubError("");
    try {
      await cancelSub();
      setShowCancelConfirm(false);
    } catch (err) {
      setSubError(extractErrorDetail(err, "Failed to cancel subscription. Please try again."));
    } finally {
      setIsCancelling(false);
    }
  }, [cancelSub]);

  // Fetch saved tests for tutors
  useEffect(() => {
    if (!isTutor) return;
    let cancelled = false;
    setSavedTestsLoading(true);
    getSavedTests()
      .then((tests) => { if (!cancelled) setSavedTests(tests); })
      .catch(() => { if (!cancelled) setSavedTests([]); })
      .finally(() => { if (!cancelled) setSavedTestsLoading(false); });
    return () => { cancelled = true; };
  }, [isTutor]);

  const handleDeleteSavedTest = useCallback(async (testId: string) => {
    try {
      await deleteSavedTest(testId);
      setSavedTests((prev) => prev.filter((t) => t.id !== testId));
    } catch {
      setSubError("Failed to delete saved test");
    }
  }, []);

  const filteredTests = savedTests.filter((t) =>
    t.test_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  function formatDate(dateStr: string | null): string {
    if (!dateStr) return "N/A";
    try {
      return new Date(dateStr).toLocaleDateString(undefined, {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    } catch {
      return "N/A";
    }
  }

  return (
    <section className="page-enter">
      {/* Welcome banner */}
      <div className="full-bleed" style={bannerStyle}>
        <h1 style={bannerHeadingStyle}>Welcome back</h1>
        <p style={bannerEmailStyle}>{user?.email}</p>
        {isSubscribed && plan && (
          <span style={{
            display: "inline-block",
            marginTop: "var(--space-2)",
            background: "rgba(255,255,255,0.15)",
            color: "#99f6e4",
            padding: "2px var(--space-3)",
            borderRadius: "var(--radius-full)",
            fontSize: "var(--font-size-xs)",
            fontWeight: 600,
          }}>
            {plan.toUpperCase()} PLAN
          </span>
        )}
      </div>

      {/* Content area */}
      <div style={contentAreaStyle}>
        {subError && (
          <div aria-live="polite" role="alert" style={errorBoxStyle}>
            {subError}
          </div>
        )}

        {subLoading ? (
          <div style={{ textAlign: "center", padding: "var(--space-6)" }} role="status" aria-label="Loading subscription status">
            <p style={{ color: "var(--text-secondary)" }}>Loading subscription status...</p>
          </div>
        ) : isSubscribed ? (
          <>
            {/* Quick action card */}
            <div style={quickActionCardStyle}>
              <p style={{ fontSize: "var(--font-size-base)", fontWeight: 600, color: "var(--color-primary-900)", marginBottom: "var(--space-2)" }}>
                Ready to practice?
              </p>
              <p style={{ fontSize: "var(--font-size-sm)", color: "var(--text-secondary)", marginBottom: "var(--space-4)" }}>
                Generate a new math test in seconds
              </p>
              <button
                type="button"
                className="btn-primary"
                onClick={() => navigate("/generate")}
                aria-label="Generate new test"
              >
                Generate New Test
              </button>
            </div>

            {/* Saved Tests — tutor only */}
            {isTutor && (
              <div style={{
                backgroundColor: "var(--bg-card)",
                boxShadow: "var(--shadow-card)",
                borderRadius: "var(--radius-lg)",
                marginBottom: "var(--space-4)",
                overflow: "hidden",
              }}>
                <div style={{ padding: "var(--space-5) var(--space-5) var(--space-3)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-3)" }}>
                    <p style={sectionLabelStyle}>SAVED TESTS</p>
                    <span style={{ fontSize: "var(--font-size-xs)", color: "var(--text-muted)" }}>
                      {savedTests.length} of 100
                    </span>
                  </div>
                  <div style={{ position: "relative" }}>
                    <Search size={14} style={{ position: "absolute", left: "var(--space-3)", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} aria-hidden="true" />
                    <input
                      type="text"
                      placeholder="Search saved tests..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      style={{
                        width: "100%",
                        padding: "var(--space-2) var(--space-4) var(--space-2) var(--space-8)",
                        fontFamily: "var(--font-family)",
                        fontSize: "var(--font-size-sm)",
                        color: "var(--text-primary)",
                        backgroundColor: "var(--bg-card)",
                        border: "1.5px solid var(--color-stone-300)",
                        borderRadius: "var(--radius-md)",
                      }}
                      aria-label="Search saved tests"
                    />
                  </div>
                </div>
                {savedTestsLoading ? (
                  <p style={{ padding: "var(--space-4) var(--space-5)", color: "var(--text-secondary)", fontSize: "var(--font-size-sm)" }}>
                    Loading saved tests...
                  </p>
                ) : filteredTests.length === 0 ? (
                  <p style={{ padding: "var(--space-4) var(--space-5)", color: "var(--text-secondary)", fontSize: "var(--font-size-sm)" }}>
                    {savedTests.length === 0 ? "No saved tests yet. Generate a test and save it from the preview page." : "No tests match your search."}
                  </p>
                ) : (
                  <div>
                    {filteredTests.map((test) => (
                      <div
                        key={test.id}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          padding: "var(--space-4) var(--space-5)",
                          borderTop: "1px solid var(--color-stone-100)",
                          cursor: "pointer",
                          transition: "background 150ms ease",
                        }}
                        onClick={() => navigate(`/saved-test/${test.id}`)}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => { if (e.key === "Enter") navigate(`/saved-test/${test.id}`); }}
                        aria-label={`Replay ${test.test_name}`}
                      >
                        <div>
                          <div style={{ fontWeight: 600, color: "var(--text-primary)", marginBottom: 2 }}>{test.test_name}</div>
                          <div style={{ fontSize: "var(--font-size-xs)", color: "var(--text-secondary)", display: "flex", gap: "var(--space-3)", flexWrap: "wrap" }}>
                            <span style={{ background: "var(--color-stone-100)", padding: "1px var(--space-2)", borderRadius: "var(--radius-full)" }}>
                              {test.config.topics.join(", ")}
                            </span>
                            <span style={{ background: "var(--color-stone-100)", padding: "1px var(--space-2)", borderRadius: "var(--radius-full)" }}>
                              {test.config.difficulty.charAt(0).toUpperCase() + test.config.difficulty.slice(1)}
                            </span>
                            <span style={{ background: "var(--color-stone-100)", padding: "1px var(--space-2)", borderRadius: "var(--radius-full)" }}>
                              {test.question_count} questions
                            </span>
                            <span>
                              {new Date(test.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
                            </span>
                          </div>
                        </div>
                        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)", flexShrink: 0 }}>
                          <button
                            type="button"
                            onClick={(e) => { e.stopPropagation(); handleDeleteSavedTest(test.id); }}
                            style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", padding: "var(--space-1)" }}
                            aria-label={`Delete ${test.test_name}`}
                          >
                            <Trash2 size={14} />
                          </button>
                          <span style={{ fontSize: "var(--font-size-sm)", fontWeight: 500, color: "var(--color-primary-700)" }}>
                            Replay <ChevronRight size={14} style={{ verticalAlign: "middle" }} />
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Subscription card */}
            <div style={subscriptionCardStyle}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <p style={{ ...sectionLabelStyle, marginBottom: "var(--space-2)" }}>SUBSCRIPTION</p>
                  <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)", marginBottom: "var(--space-1)" }}>
                    <span style={{ display: "inline-block", width: 8, height: 8, borderRadius: "50%", backgroundColor: "#10b981" }} />
                    <span style={{ fontWeight: 600, color: "var(--color-primary-900)" }} role="status">
                      Active{plan ? ` — ${plan.charAt(0).toUpperCase() + plan.slice(1)} Plan` : ""}
                    </span>
                  </div>
                  {subscription?.current_period_end && (
                    <p style={{ fontSize: "var(--font-size-sm)", color: "var(--text-secondary)" }}>
                      Current period ends: {formatDate(subscription.current_period_end)}
                    </p>
                  )}
                </div>
                <div>
                  {!showCancelConfirm ? (
                    <button
                      type="button"
                      style={{
                        ...dangerBtnStyle,
                        fontSize: "var(--font-size-sm)",
                        padding: "var(--space-2) var(--space-4)",
                      }}
                      onClick={() => setShowCancelConfirm(true)}
                      aria-label="Cancel subscription"
                    >
                      Cancel Subscription
                    </button>
                  ) : null}
                </div>
              </div>
              {showCancelConfirm && (
                <div style={confirmBoxStyle} aria-live="polite">
                  <p style={{ marginBottom: "var(--space-3)", color: "var(--text-primary)", fontSize: "var(--font-size-sm)" }}>
                    Your subscription will remain active until the end of the current billing period.
                    Are you sure you want to cancel?
                  </p>
                  <div style={{ display: "flex", gap: "var(--space-2)" }}>
                    <button
                      type="button"
                      style={{
                        ...dangerBtnStyle,
                        backgroundColor: "var(--color-error-text)",
                        color: "var(--text-on-primary)",
                        borderColor: "var(--color-error-text)",
                      }}
                      onClick={handleCancelSub}
                      disabled={isCancelling}
                      aria-label="Confirm cancel subscription"
                    >
                      {isCancelling ? "Cancelling..." : "Yes, cancel subscription"}
                    </button>
                    <button
                      type="button"
                      className="btn-secondary"
                      onClick={() => setShowCancelConfirm(false)}
                      disabled={isCancelling}
                    >
                      Keep Subscription
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Streak card */}
            <div style={streakCardStyle}>
              {stats && stats.streak_current > 0 ? (
                <>
                  <div>
                    <div style={streakLeftStyle}>
                      <Flame
                        size={24}
                        fill="currentColor"
                        className={stats.is_active_today ? "flame-active" : "flame-inactive"}
                        aria-hidden="true"
                      />
                      <span
                        style={streakNumberStyle}
                        aria-label={`${stats.streak_current} day practice streak`}
                      >
                        {stats.streak_current}
                      </span>
                      <span style={streakLabelStyle}>day streak</span>
                    </div>
                    <div style={dotsRowStyle}>
                      {Array.from({ length: 7 }, (_, i) => {
                        const filled = i < Math.min(stats.streak_current, 7);
                        const isToday = i === 6;
                        return (
                          <span
                            key={i}
                            aria-hidden="true"
                            style={{
                              width: 8,
                              height: 8,
                              borderRadius: "50%",
                              backgroundColor: filled
                                ? isToday && stats.is_active_today
                                  ? "var(--color-accent-500)"
                                  : "var(--color-accent-400)"
                                : "transparent",
                              border: filled ? "none" : "1.5px solid var(--color-stone-300)",
                            }}
                          />
                        );
                      })}
                    </div>
                  </div>
                  <div style={bestStreakStyle}>
                    <Trophy size={16} style={{ color: "var(--color-accent-400)" }} aria-hidden="true" />
                    <span>Best: {stats.streak_best} days</span>
                  </div>
                </>
              ) : (
                <div style={streakLeftStyle}>
                  <Flame size={24} className="flame-inactive" aria-hidden="true" />
                  <span style={{ ...streakLabelStyle, fontWeight: 500 }}>Start your streak</span>
                </div>
              )}
            </div>

            {/* Stats row */}
            <div style={statsRowStyle}>
              <div className="stat-pop" style={statCardStyle}>
                <FileText
                  size={20}
                  style={{ color: "var(--color-primary-500)", marginBottom: "var(--space-2)" }}
                  aria-hidden="true"
                />
                <p style={{ fontSize: "var(--font-size-xl)", fontWeight: 800, color: "var(--color-primary-600)" }}>
                  {statsLoading ? "--" : stats?.tests_generated ?? 0}
                </p>
                <p style={{ fontSize: "var(--font-size-xs)", color: "var(--text-secondary)" }}>Tests Generated</p>
              </div>
              <div className="stat-pop" style={statCardStyle}>
                <BookOpen
                  size={20}
                  style={{ color: "var(--color-primary-500)", marginBottom: "var(--space-2)" }}
                  aria-hidden="true"
                />
                <p style={{ fontSize: "var(--font-size-xl)", fontWeight: 800, color: "var(--color-primary-600)" }}>
                  {statsLoading ? "--" : stats?.questions_generated ?? 0}
                </p>
                <p style={{ fontSize: "var(--font-size-xs)", color: "var(--text-secondary)" }}>Questions Practiced</p>
              </div>
            </div>

            {/* Topic mastery map */}
            {stats && stats.questions_generated > 0 ? (
              <div style={masteryCardStyle} aria-label="Practice distribution by topic">
                <p style={sectionLabelStyle}>PRACTICE DISTRIBUTION</p>
                {Object.entries(stats.topic_counts)
                  .sort(([, a], [, b]) => b - a)
                  .map(([topic, count]) => {
                    const maxCount = Math.max(...Object.values(stats.topic_counts));
                    const colors = TOPIC_COLORS[topic] || {
                      bar: "var(--color-primary-500)",
                      text: "var(--color-primary-700)",
                    };
                    const pct = maxCount > 0 ? (count / maxCount) * 100 : 0;
                    return (
                      <div key={topic} style={topicRowStyle}>
                        <div style={barContainerStyle}>
                          <div
                            role="meter"
                            aria-valuenow={count}
                            aria-valuemin={0}
                            aria-valuemax={maxCount}
                            aria-label={`${topic}: ${count} questions`}
                            style={{
                              height: "100%",
                              width: `${Math.max(pct, 4)}%`,
                              backgroundColor: colors.bar,
                              borderRadius: "var(--radius-full)",
                              transition: "width var(--transition-normal)",
                            }}
                          />
                        </div>
                        <span style={{
                          fontSize: "var(--font-size-sm)",
                          color: colors.text,
                          minWidth: 90,
                          textTransform: "capitalize",
                        }}>
                          {topic}
                        </span>
                        <span style={{
                          fontSize: "var(--font-size-sm)",
                          fontWeight: 700,
                          color: "var(--text-primary)",
                          minWidth: 30,
                          textAlign: "right",
                        }}>
                          {count}
                        </span>
                      </div>
                    );
                  })}
              </div>
            ) : stats && stats.questions_generated === 0 ? (
              <div style={masteryCardStyle}>
                <p style={sectionLabelStyle}>PRACTICE DISTRIBUTION</p>
                <p style={{ color: "var(--text-secondary)", fontSize: "var(--font-size-sm)" }}>
                  Generate your first test to see your practice breakdown
                </p>
              </div>
            ) : null}

            {/* Account section */}
            <div style={accountCardStyle}>
              <p style={sectionLabelStyle}>ACCOUNT</p>
              <button
                type="button"
                style={{
                  ...accountRowStyle,
                  borderBottom: "1px solid var(--color-stone-100)",
                  color: "var(--text-primary)",
                }}
                onClick={handleLogout}
                aria-label="Sign out"
              >
                <span>Sign Out</span>
                <ChevronRight size={16} style={{ color: "var(--text-muted)" }} />
              </button>

              {!showConfirm ? (
                <button
                  type="button"
                  style={{
                    ...accountRowStyle,
                    color: "var(--color-error-text)",
                  }}
                  onClick={() => setShowConfirm(true)}
                >
                  <span>Delete Account</span>
                  <ChevronRight size={16} style={{ color: "var(--text-muted)" }} />
                </button>
              ) : (
                <div style={confirmBoxStyle} aria-live="polite">
                  <p style={{ marginBottom: "var(--space-3)", color: "var(--text-primary)" }}>
                    Are you sure? This action cannot be undone.
                  </p>
                  <div style={{ display: "flex", gap: "var(--space-2)" }}>
                    <button
                      type="button"
                      style={{
                        ...dangerBtnStyle,
                        backgroundColor: "var(--color-error-text)",
                        color: "var(--text-on-primary)",
                        borderColor: "var(--color-error-text)",
                      }}
                      onClick={handleDeleteAccount}
                      disabled={isDeleting}
                    >
                      {isDeleting ? "Deleting..." : "Yes, delete my account"}
                    </button>
                    <button
                      type="button"
                      className="btn-secondary"
                      onClick={() => setShowConfirm(false)}
                      disabled={isDeleting}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          </>
        ) : (
          <>
            {/* Plan comparison */}
            <div style={{ marginBottom: "var(--space-4)" }}>
              <p style={sectionLabelStyle}>CHOOSE YOUR PLAN</p>
              <div style={{ display: "flex", gap: "var(--space-4)" }}>
                {/* Student */}
                <div style={{
                  flex: 1, background: "var(--bg-card)", borderRadius: "var(--radius-lg)",
                  boxShadow: "var(--shadow-card)", padding: "var(--space-6)",
                  border: "2px solid transparent",
                }}>
                  <p style={{ fontSize: "var(--font-size-lg)", fontWeight: 700, color: "var(--color-primary-900)", marginBottom: "var(--space-1)" }}>Student</p>
                  <p style={{ fontSize: "var(--font-size-2xl)", fontWeight: 800, color: "var(--color-accent-600)", marginBottom: "var(--space-1)" }}>$5</p>
                  <p style={{ fontSize: "var(--font-size-sm)", color: "var(--text-secondary)", marginBottom: "var(--space-4)" }}>CAD / month</p>
                  <ul style={{ listStyle: "none", padding: 0, marginBottom: "var(--space-4)" }}>
                    {["Unlimited test generation", "10+ math topics", "Step-by-step solutions", "PDF downloads", "Practice streak tracking"].map((f) => (
                      <li key={f} style={{ fontSize: "var(--font-size-sm)", color: "var(--text-secondary)", padding: "var(--space-1) 0", display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
                        <span style={{ display: "inline-block", width: 6, height: 6, borderRadius: "50%", background: "var(--color-primary-500)", flexShrink: 0 }} />
                        {f}
                      </li>
                    ))}
                  </ul>
                  <button
                    type="button"
                    className="btn-secondary"
                    style={{ width: "100%" }}
                    onClick={() => handleSubscribe("student")}
                    disabled={isSubscribing}
                  >
                    {isSubscribing ? "Redirecting..." : "Choose Student"}
                  </button>
                </div>
                {/* Tutor */}
                <div style={{
                  flex: 1, background: "var(--bg-card)", borderRadius: "var(--radius-lg)",
                  boxShadow: "var(--shadow-card)", padding: "var(--space-6)",
                  border: "2px solid var(--color-accent-500)", position: "relative",
                }}>
                  <span style={{
                    position: "absolute", top: -10, right: "var(--space-4)",
                    background: "var(--color-accent-500)", color: "#fff",
                    fontSize: "var(--font-size-xs)", fontWeight: 600,
                    padding: "2px var(--space-3)", borderRadius: "var(--radius-full)",
                  }}>BEST VALUE</span>
                  <p style={{ fontSize: "var(--font-size-lg)", fontWeight: 700, color: "var(--color-primary-900)", marginBottom: "var(--space-1)" }}>Tutor</p>
                  <p style={{ fontSize: "var(--font-size-2xl)", fontWeight: 800, color: "var(--color-accent-600)", marginBottom: "var(--space-1)" }}>$12.99</p>
                  <p style={{ fontSize: "var(--font-size-sm)", color: "var(--text-secondary)", marginBottom: "var(--space-4)" }}>CAD / month</p>
                  <ul style={{ listStyle: "none", padding: 0, marginBottom: "var(--space-4)" }}>
                    <li style={{ fontSize: "var(--font-size-sm)", color: "var(--text-secondary)", padding: "var(--space-1) 0", display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
                      <span style={{ display: "inline-block", width: 6, height: 6, borderRadius: "50%", background: "var(--color-primary-500)", flexShrink: 0 }} />
                      Everything in Student, plus:
                    </li>
                    {["Save up to 100 tests", "Name and organize tests", "Instant replay", "Search saved tests"].map((f) => (
                      <li key={f} style={{ fontSize: "var(--font-size-sm)", color: "var(--color-primary-700)", fontWeight: 500, padding: "var(--space-1) 0", display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
                        <span style={{ display: "inline-block", width: 6, height: 6, borderRadius: "50%", background: "var(--color-accent-500)", flexShrink: 0 }} />
                        {f}
                      </li>
                    ))}
                  </ul>
                  <button
                    type="button"
                    className="btn-primary"
                    style={{ width: "100%" }}
                    onClick={() => handleSubscribe("tutor")}
                    disabled={isSubscribing}
                  >
                    {isSubscribing ? "Redirecting..." : "Choose Tutor"}
                  </button>
                </div>
              </div>
            </div>

            {/* Account section (non-subscribed) */}
            <div style={accountCardStyle}>
              <p style={sectionLabelStyle}>ACCOUNT</p>
              <button
                type="button"
                style={{
                  ...accountRowStyle,
                  borderBottom: "1px solid var(--color-stone-100)",
                  color: "var(--text-primary)",
                }}
                onClick={handleLogout}
                aria-label="Sign out"
              >
                <span>Sign Out</span>
                <ChevronRight size={16} style={{ color: "var(--text-muted)" }} />
              </button>

              {!showConfirm ? (
                <button
                  type="button"
                  style={{
                    ...accountRowStyle,
                    color: "var(--color-error-text)",
                  }}
                  onClick={() => setShowConfirm(true)}
                >
                  <span>Delete Account</span>
                  <ChevronRight size={16} style={{ color: "var(--text-muted)" }} />
                </button>
              ) : (
                <div style={confirmBoxStyle} aria-live="polite">
                  <p style={{ marginBottom: "var(--space-3)", color: "var(--text-primary)" }}>
                    Are you sure? This action cannot be undone.
                  </p>
                  <div style={{ display: "flex", gap: "var(--space-2)" }}>
                    <button
                      type="button"
                      style={{
                        ...dangerBtnStyle,
                        backgroundColor: "var(--color-error-text)",
                        color: "var(--text-on-primary)",
                        borderColor: "var(--color-error-text)",
                      }}
                      onClick={handleDeleteAccount}
                      disabled={isDeleting}
                    >
                      {isDeleting ? "Deleting..." : "Yes, delete my account"}
                    </button>
                    <button
                      type="button"
                      className="btn-secondary"
                      onClick={() => setShowConfirm(false)}
                      disabled={isDeleting}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </section>
  );
}
