import { useState, useRef, useEffect, useCallback } from "react";

type TimerState = "idle" | "running" | "paused";

interface TimerProps {
  previousDuration: number | null;
  onTimerComplete: (durationSeconds: number) => void;
}

function formatTime(totalSeconds: number): string {
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = totalSeconds % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

/* Styles — dark-on-dark for embedding in the teal summary bar */

const timerGroupStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "var(--space-3)",
  background: "rgba(0,0,0,0.2)",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: "var(--radius-md)",
  padding: "8px 16px",
};

const previousStyle: React.CSSProperties = {
  fontSize: "var(--font-size-sm)",
  color: "#ffffff",
  fontWeight: 600,
};

const sepStyle: React.CSSProperties = {
  color: "rgba(255,255,255,0.25)",
};

const digitsStyle: React.CSSProperties = {
  fontVariantNumeric: "tabular-nums lining-nums",
  fontSize: "1.1rem",
  fontWeight: 700,
  color: "#ffffff",
  minWidth: "6.5ch",
  textAlign: "center",
};

const btnStyle: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  width: "34px",
  height: "34px",
  padding: 0,
  borderRadius: "8px",
  border: "1.5px solid rgba(255,255,255,0.25)",
  background: "rgba(255,255,255,0.12)",
  fontSize: "0.85rem",
  cursor: "pointer",
  color: "#ffffff",
  lineHeight: 1,
};

const stopBtnStyle: React.CSSProperties = {
  ...btnStyle,
  borderColor: "rgba(252,165,165,0.6)",
  background: "rgba(220,38,38,0.25)",
  color: "#fecaca",
};

export default function Timer({ previousDuration, onTimerComplete }: TimerProps) {
  const [timerState, setTimerState] = useState<TimerState>("idle");
  const [displaySeconds, setDisplaySeconds] = useState(0);
  const [announcement, setAnnouncement] = useState("");

  const startTimeRef = useRef(0);
  const pausedAccumRef = useRef(0);
  const pausedAtRef = useRef(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearTimer = useCallback(() => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const tick = useCallback(() => {
    const elapsed = Date.now() - startTimeRef.current - pausedAccumRef.current;
    setDisplaySeconds(Math.floor(elapsed / 1000));
  }, []);

  const startInterval = useCallback(() => {
    clearTimer();
    intervalRef.current = setInterval(tick, 250);
  }, [clearTimer, tick]);

  function handleStart() {
    startTimeRef.current = Date.now();
    pausedAccumRef.current = 0;
    pausedAtRef.current = 0;
    setDisplaySeconds(0);
    setTimerState("running");
    startInterval();
    announce("Timer started");
  }

  function handleStop() {
    clearTimer();
    const elapsed = Date.now() - startTimeRef.current - pausedAccumRef.current;
    const finalSeconds = Math.max(1, Math.floor(elapsed / 1000));
    setTimerState("idle");
    setDisplaySeconds(0);
    onTimerComplete(finalSeconds);
    announce("Timer stopped, duration saved");
  }

  function handlePause() {
    clearTimer();
    pausedAtRef.current = Date.now();
    setTimerState("paused");
    announce("Timer paused");
  }

  function handleResume() {
    pausedAccumRef.current += Date.now() - pausedAtRef.current;
    pausedAtRef.current = 0;
    setTimerState("running");
    startInterval();
    announce("Timer resumed");
  }

  function announce(msg: string) {
    setAnnouncement("");
    setTimeout(() => setAnnouncement(msg), 100);
  }

  // beforeunload guard
  useEffect(() => {
    if (timerState === "idle") return;

    function handleBeforeUnload(e: BeforeUnloadEvent) {
      e.preventDefault();
      e.returnValue = true;
    }

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [timerState]);

  // Cleanup on unmount
  useEffect(() => {
    return () => clearTimer();
  }, [clearTimer]);

  // Refresh display on tab visibility change
  useEffect(() => {
    function handleVisibility() {
      if (document.visibilityState === "visible" && timerState === "running") {
        tick();
      }
    }

    document.addEventListener("visibilitychange", handleVisibility);
    return () => document.removeEventListener("visibilitychange", handleVisibility);
  }, [timerState, tick]);

  return (
    <div style={timerGroupStyle}>
      {/* Previous time */}
      <span style={previousStyle}>
        Prev: {previousDuration !== null ? formatTime(previousDuration) : "--:--:--"}
      </span>

      {/* Divider */}
      <span style={sepStyle} aria-hidden="true">|</span>

      {/* Timer display */}
      <div role="timer" aria-label="Test duration" aria-atomic="true" style={digitsStyle}>
        {formatTime(displaySeconds)}
      </div>

      {/* Controls — icon-only buttons */}
      {timerState === "idle" && (
        <button type="button" onClick={handleStart} aria-label="Start timer" style={btnStyle}>
          &#9654;
        </button>
      )}

      {timerState === "running" && (
        <>
          <button type="button" onClick={handlePause} aria-label="Pause timer" style={btnStyle}>
            &#9208;
          </button>
          <button type="button" onClick={handleStop} aria-label="Stop timer and save" style={stopBtnStyle}>
            &#9209;
          </button>
        </>
      )}

      {timerState === "paused" && (
        <>
          <button type="button" onClick={handleResume} aria-label="Resume timer" style={btnStyle}>
            &#9654;
          </button>
          <button type="button" onClick={handleStop} aria-label="Stop timer and save" style={stopBtnStyle}>
            &#9209;
          </button>
        </>
      )}

      {/* Screen reader announcements */}
      <div role="status" aria-live="polite" className="sr-only">
        {announcement}
      </div>
    </div>
  );
}

export { formatTime };
