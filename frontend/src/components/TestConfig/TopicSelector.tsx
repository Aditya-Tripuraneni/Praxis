import { useState, useCallback, useRef, useEffect, useMemo } from 'react';
import type { TopicInfo } from '../../types';

const TOPIC_COLORS: Record<string, { decorative: string; text: string; light: string }> = {
  algebra: { decorative: 'var(--color-topic-algebra)', text: 'var(--color-topic-algebra-text)', light: 'var(--color-topic-algebra-light)' },
  functions: { decorative: 'var(--color-topic-functions)', text: 'var(--color-topic-functions-text)', light: 'var(--color-topic-functions-light)' },
  geometry: { decorative: 'var(--color-topic-geometry)', text: 'var(--color-topic-geometry-text)', light: 'var(--color-topic-geometry-light)' },
  trigonometry: { decorative: 'var(--color-topic-trigonometry)', text: 'var(--color-topic-trigonometry-text)', light: 'var(--color-topic-trigonometry-light)' },
  calculus: { decorative: 'var(--color-topic-calculus)', text: 'var(--color-topic-calculus-text)', light: 'var(--color-topic-calculus-light)' },
  combinatorics: { decorative: 'var(--color-topic-combinatorics)', text: 'var(--color-topic-combinatorics-text)', light: 'var(--color-topic-combinatorics-light)' },
};

const DEFAULT_TOPIC_COLOR = { decorative: 'var(--color-primary-500)', text: 'var(--color-primary-700)', light: 'var(--color-primary-50)' };

interface TopicSelectorProps {
  topics: TopicInfo[];
  selected: string[];
  onChange: (selected: string[]) => void;
}

// --- Styles ---

const containerStyle: React.CSSProperties = {
  marginBottom: 'var(--space-6)',
};

const legendStyle: React.CSSProperties = {
  display: 'block',
  fontSize: 'var(--font-size-base)',
  fontWeight: 600,
  color: 'var(--text-primary)',
  marginBottom: 'var(--space-3)',
};

const groupListStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 'var(--space-3)',
};

const groupFieldsetStyle: React.CSSProperties = {
  border: '1px solid var(--color-stone-200)',
  borderRadius: 'var(--radius-md)',
  padding: 0,
  margin: 0,
  backgroundColor: 'var(--bg-card)',
  boxShadow: 'var(--shadow-card)',
  transition: 'box-shadow var(--transition-normal)',
};

const groupHeaderStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 'var(--space-3)',
  padding: 'var(--space-3) var(--space-4)',
  cursor: 'pointer',
  userSelect: 'none',
  background: 'none',
  border: 'none',
  width: '100%',
  textAlign: 'left',
  fontSize: 'var(--font-size-sm)',
  fontWeight: 500,
  color: 'var(--text-primary)',
  borderRadius: 'var(--radius-md)',
  transition: 'background-color var(--transition-fast)',
};

const arrowStyle = (expanded: boolean): React.CSSProperties => ({
  display: 'inline-block',
  fontSize: '0.7rem',
  transition: 'transform var(--transition-fast)',
  transform: expanded ? 'rotate(90deg)' : 'rotate(0deg)',
  color: 'var(--text-secondary)',
  flexShrink: 0,
});

const topicNameStyle: React.CSSProperties = {
  flexGrow: 1,
};

const countBadgeStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-xs)',
  color: 'var(--text-muted)',
  marginLeft: 'auto',
  flexShrink: 0,
};

const subtopicListStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 'var(--space-1)',
  padding: 'var(--space-1) var(--space-4) var(--space-3) var(--space-9)',
  borderTop: '1px solid var(--color-stone-100)',
};

const subtopicLabelStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 'var(--space-2)',
  padding: 'var(--space-1) 0',
  cursor: 'pointer',
  fontSize: 'var(--font-size-sm)',
  color: 'var(--text-secondary)',
  lineHeight: 1.5,
};

const checkboxStyle: React.CSSProperties = {
  accentColor: 'var(--color-primary-700)',
  width: '16px',
  height: '16px',
  flexShrink: 0,
};

const headerCheckboxStyle: React.CSSProperties = {
  ...checkboxStyle,
  width: '18px',
  height: '18px',
};

// --- Indeterminate Checkbox ---

function IndeterminateCheckbox({
  checked,
  indeterminate,
  onChange,
  ariaLabel,
  accentColor,
}: {
  checked: boolean;
  indeterminate: boolean;
  onChange: () => void;
  ariaLabel: string;
  accentColor?: string;
}) {
  const ref = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.indeterminate = indeterminate;
    }
  }, [indeterminate]);

  return (
    <input
      ref={ref}
      type="checkbox"
      checked={checked}
      onChange={onChange}
      aria-label={ariaLabel}
      style={accentColor ? { ...headerCheckboxStyle, accentColor } : headerCheckboxStyle}
    />
  );
}

// --- Topic Group ---

interface TopicGroupProps {
  topic: TopicInfo;
  selectedSubtopics: string[];
  onToggleTopic: (topicId: string) => void;
  onToggleSubtopic: (topicId: string, subtopicId: string) => void;
}

function TopicGroup({ topic, selectedSubtopics, onToggleTopic, onToggleSubtopic }: TopicGroupProps) {
  const [expanded, setExpanded] = useState(false);

  const allSubtopicIds = topic.subtopics.map((s) => s.id);
  const selectedCount = selectedSubtopics.length;
  const totalCount = allSubtopicIds.length;
  const allSelected = totalCount > 0 && selectedCount === totalCount;
  const someSelected = selectedCount > 0 && selectedCount < totalCount;

  const colors = TOPIC_COLORS[topic.name.toLowerCase()] || DEFAULT_TOPIC_COLOR;

  const handleHeaderClick = useCallback(() => {
    setExpanded((prev) => !prev);
  }, []);

  const handleTopicCheckboxToggle = useCallback(() => {
    onToggleTopic(topic.id);
  }, [onToggleTopic, topic.id]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        setExpanded((prev) => !prev);
      }
    },
    [],
  );

  const selectedLabel = selectedCount > 0 ? ` (${selectedCount}/${totalCount} selected)` : '';

  return (
    <fieldset style={{ ...groupFieldsetStyle, borderLeft: '3px solid ' + colors.decorative }}>
      <legend style={{ position: 'absolute', width: '1px', height: '1px', overflow: 'hidden', clip: 'rect(0,0,0,0)' }}>
        {topic.name}
      </legend>
      <div
        style={groupHeaderStyle}
        role="button"
        tabIndex={0}
        onClick={handleHeaderClick}
        onKeyDown={handleKeyDown}
        aria-expanded={expanded}
      >
        <span aria-hidden="true" style={{ ...arrowStyle(expanded), color: colors.decorative }}>&#9654;</span>
        {/* Stop checkbox click from toggling expand/collapse */}
        <span onClick={(e) => e.stopPropagation()}>
          <IndeterminateCheckbox
            checked={allSelected}
            indeterminate={someSelected}
            onChange={handleTopicCheckboxToggle}
            ariaLabel={`Select all ${topic.name} subtopics`}
            accentColor={colors.decorative}
          />
        </span>
        <span style={topicNameStyle}>{topic.name}</span>
        <span style={{
          ...countBadgeStyle,
          color: colors.text,
          backgroundColor: colors.light,
          padding: 'var(--space-1) var(--space-2)',
          borderRadius: 'var(--radius-full)',
          fontSize: 'var(--font-size-xs)',
          fontWeight: 500,
        }}>
          {topic.template_count} template{topic.template_count !== 1 ? 's' : ''}
          {selectedLabel}
        </span>
      </div>

      {expanded && (
        <div style={subtopicListStyle} role="group" aria-label={`${topic.name} subtopics`}>
          {topic.subtopics.map((subtopic) => {
            const isChecked = selectedSubtopics.includes(subtopic.id);
            return (
              <label key={subtopic.id} style={subtopicLabelStyle}>
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => onToggleSubtopic(topic.id, subtopic.id)}
                  style={{ ...checkboxStyle, accentColor: colors.decorative }}
                />
                {subtopic.name}
              </label>
            );
          })}
        </div>
      )}
    </fieldset>
  );
}

// --- Main Component ---

/**
 * TopicSelector with granular subtopic selection.
 *
 * `selected` contains dot-notation strings like "algebra.linear_equations"
 * or bare topic names like "algebra" when all subtopics are selected.
 */
export default function TopicSelector({ topics, selected, onChange }: TopicSelectorProps) {
  // Parse `selected` into a map: topicId -> Set of selected subtopicIds (or null = all)
  const selectionMap = useMemo(() => parseSelection(selected, topics), [selected, topics]);

  const handleToggleTopic = useCallback(
    (topicId: string) => {
      const topic = topics.find((t) => t.id === topicId);
      if (!topic) return;

      const current = selectionMap.get(topicId);
      const allIds = topic.subtopics.map((s) => s.id);

      let newMap: Map<string, Set<string>>;
      if (current && current.size === allIds.length) {
        // All selected -> deselect all
        newMap = new Map(selectionMap);
        newMap.delete(topicId);
      } else {
        // None or some selected -> select all
        newMap = new Map(selectionMap);
        newMap.set(topicId, new Set(allIds));
      }

      onChange(serializeSelection(newMap, topics));
    },
    [topics, selectionMap, onChange],
  );

  const handleToggleSubtopic = useCallback(
    (topicId: string, subtopicId: string) => {
      const topic = topics.find((t) => t.id === topicId);
      if (!topic) return;

      const current = selectionMap.get(topicId) ?? new Set<string>();
      const newSet = new Set(current);

      if (newSet.has(subtopicId)) {
        newSet.delete(subtopicId);
      } else {
        newSet.add(subtopicId);
      }

      const newMap = new Map(selectionMap);
      if (newSet.size === 0) {
        newMap.delete(topicId);
      } else {
        newMap.set(topicId, newSet);
      }

      onChange(serializeSelection(newMap, topics));
    },
    [topics, selectionMap, onChange],
  );

  return (
    <fieldset style={containerStyle}>
      <legend style={legendStyle}>Topics</legend>
      <div style={groupListStyle}>
        {topics.map((topic) => {
          const selectedSubs = selectionMap.get(topic.id);
          const selectedSubtopics = selectedSubs ? Array.from(selectedSubs) : [];

          return (
            <TopicGroup
              key={topic.id}
              topic={topic}
              selectedSubtopics={selectedSubtopics}
              onToggleTopic={handleToggleTopic}
              onToggleSubtopic={handleToggleSubtopic}
            />
          );
        })}
      </div>
    </fieldset>
  );
}

// --- Helpers ---

/**
 * Parse the `selected` array into a map of topicId -> Set<subtopicId>.
 * Bare topic names (e.g. "algebra") expand to all subtopics of that topic.
 * Dot-notation (e.g. "algebra.linear_equations") maps to specific subtopics.
 */
function parseSelection(
  selected: string[],
  topics: TopicInfo[],
): Map<string, Set<string>> {
  const map = new Map<string, Set<string>>();

  for (const entry of selected) {
    const dotIndex = entry.indexOf('.');
    if (dotIndex === -1) {
      // Bare topic name -> all subtopics
      const topic = topics.find((t) => t.id === entry);
      if (topic) {
        map.set(entry, new Set(topic.subtopics.map((s) => s.id)));
      }
    } else {
      const topicId = entry.substring(0, dotIndex);
      const subtopicId = entry.substring(dotIndex + 1);
      if (!map.has(topicId)) {
        map.set(topicId, new Set());
      }
      map.get(topicId)!.add(subtopicId);
    }
  }

  return map;
}

/**
 * Serialize the selection map back to the string array format.
 * If all subtopics of a topic are selected, emit the bare topic name.
 * Otherwise, emit dot-notation for each selected subtopic.
 */
function serializeSelection(
  map: Map<string, Set<string>>,
  topics: TopicInfo[],
): string[] {
  const result: string[] = [];

  for (const [topicId, subtopicIds] of map) {
    if (subtopicIds.size === 0) continue;

    const topic = topics.find((t) => t.id === topicId);
    if (!topic) continue;

    const allIds = topic.subtopics.map((s) => s.id);
    if (subtopicIds.size === allIds.length && allIds.every((id) => subtopicIds.has(id))) {
      // All selected -> bare topic name
      result.push(topicId);
    } else {
      // Partial -> dot-notation
      for (const subId of subtopicIds) {
        result.push(`${topicId}.${subId}`);
      }
    }
  }

  return result;
}
