import React from "react";

type Variant = "full" | "icon";
type ColorScheme = "dark" | "light" | "mono";

interface PraxisLogoProps {
  /** "full" = icon + wordmark, "icon" = standalone mark only */
  variant?: Variant;
  /** "dark" = for dark backgrounds (nav), "light" = for light/white backgrounds, "mono" = single color */
  colorScheme?: ColorScheme;
  /** Height in pixels — width scales proportionally */
  height?: number;
  className?: string;
  style?: React.CSSProperties;
}

const COLORS: Record<ColorScheme, { square: string; squareFill: string; x: string; dot: string; text: string }> = {
  dark: {
    square: "#5eead4",
    squareFill: "rgba(94,234,212,0.15)",
    x: "#5eead4",
    dot: "#f97316",
    text: "#5eead4",
  },
  light: {
    square: "#134e4a",
    squareFill: "none",
    x: "#0d9488",
    dot: "#f97316",
    text: "#134e4a",
  },
  mono: {
    square: "currentColor",
    squareFill: "none",
    x: "currentColor",
    dot: "currentColor",
    text: "currentColor",
  },
};

function IconMark({ colors, size }: { colors: typeof COLORS.dark; size: number }) {
  return (
    <svg
      viewBox="0 0 48 48"
      width={size}
      height={size}
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <rect x="2" y="2" width="44" height="44" rx="10" fill={colors.squareFill} stroke={colors.square} strokeWidth="2.5" />
      <line x1="14" y1="14" x2="34" y2="34" stroke={colors.x} strokeWidth="5" strokeLinecap="round" />
      <line x1="34" y1="14" x2="14" y2="34" stroke={colors.x} strokeWidth="5" strokeLinecap="round" />
      <circle cx="24" cy="24" r="3" fill={colors.dot} />
    </svg>
  );
}

export default function PraxisLogo({
  variant = "full",
  colorScheme = "light",
  height = 28,
  className,
  style,
}: PraxisLogoProps) {
  const colors = COLORS[colorScheme];

  if (variant === "icon") {
    return <IconMark colors={colors} size={height} />;
  }

  // Full variant: icon + wordmark
  const iconSize = height;
  const fontSize = height * 0.85;

  return (
    <span
      className={className}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: height * 0.3,
        ...style,
      }}
    >
      <IconMark colors={colors} size={iconSize} />
      <span
        style={{
          fontFamily: "var(--font-family)",
          fontSize,
          fontWeight: 700,
          color: colors.text,
          letterSpacing: "0.02em",
          lineHeight: 1,
        }}
      >
        Praxis
      </span>
    </span>
  );
}
