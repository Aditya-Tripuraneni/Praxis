function titleCaseWords(value: string): string {
  return value
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}

export function formatTopicId(topicId: string): string {
  return titleCaseWords(topicId.replace(/_/g, " "));
}

export function formatSubtopicId(subtopicId: string): string {
  return titleCaseWords(subtopicId.replace(/_/g, " "));
}

export function formatDifficultyId(difficulty: string): string {
  return titleCaseWords(difficulty.replace(/_/g, " "));
}

export function formatTopicSelection(selection: string): string {
  const dotIndex = selection.indexOf(".");
  if (dotIndex === -1) {
    return formatTopicId(selection);
  }
  return formatSubtopicId(selection.slice(dotIndex + 1));
}
