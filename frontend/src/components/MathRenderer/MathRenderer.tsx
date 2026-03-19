import React, { useMemo } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";

interface MathRendererProps {
  latex: string;
  displayMode?: boolean;
}

/**
 * Split a string containing mixed text and $...$ math into segments.
 * Returns alternating [text, math, text, math, ...] where math parts
 * have their $ delimiters stripped.
 */
function parseSegments(input: string): { text: string; isMath: boolean; isDisplay: boolean }[] {
  const parts: { text: string; isMath: boolean; isDisplay: boolean }[] = [];
  const regex = /\$\$([^$]+)\$\$|\$([^$]+)\$/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(input)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ text: input.slice(lastIndex, match.index), isMath: false, isDisplay: false });
    }
    // group 1 = $$ (display), group 2 = $ (inline)
    const isDisplay = match[1] != null;
    const mathContent = match[1] || match[2];
    parts.push({ text: mathContent, isMath: true, isDisplay });
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < input.length) {
    parts.push({ text: input.slice(lastIndex), isMath: false, isDisplay: false });
  }

  return parts;
}

function renderMath(tex: string, displayMode: boolean): string {
  return katex.renderToString(tex, {
    displayMode,
    throwOnError: false,
    strict: "warn",
  });
}

const MathRenderer: React.FC<MathRendererProps> = React.memo(
  ({ latex, displayMode = false }) => {
    const segments = useMemo(() => parseSegments(latex), [latex]);

    // If the whole string is pure math (no $ delimiters found, or single
    // expression), try rendering it as-is for backwards compatibility
    if (segments.length === 1 && !segments[0].isMath) {
      // No $ delimiters found — try as raw KaTeX
      const stripped = latex.trim().replace(/^\$+|\$+$/g, "").trim();
      if (stripped) {
        try {
          const html = renderMath(stripped, displayMode);
          return <span dangerouslySetInnerHTML={{ __html: html }} />;
        } catch {
          return <span>{latex}</span>;
        }
      }
      return <span>{latex}</span>;
    }

    return (
      <span>
        {segments.map((seg, i) =>
          seg.isMath ? (
            <span
              key={i}
              dangerouslySetInnerHTML={{ __html: renderMath(seg.text, seg.isDisplay) }}
            />
          ) : (
            <span key={i}>{seg.text}</span>
          )
        )}
      </span>
    );
  }
);

MathRenderer.displayName = "MathRenderer";

export default MathRenderer;
