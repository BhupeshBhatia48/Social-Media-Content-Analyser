/**
 * Word-level diff between an original and improved text.
 * Returns an array of { type: 'same' | 'del' | 'add', text } tokens,
 * used to render inline track-changes markup in the "Detailed Changes"
 * accordion of each analysis card.
 */
export function tokenize(text) {
  return text.split(/(\s+)/).filter((t) => t.length > 0);
}

export function diffWords(originalText, improvedText) {
  const a = tokenize(originalText);
  const b = tokenize(improvedText);
  const n = a.length;
  const m = b.length;

  const dp = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      dp[i][j] =
        a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
    }
  }

  let i = 0;
  let j = 0;
  const parts = [];
  while (i < n && j < m) {
    if (a[i] === b[j]) {
      parts.push({ type: "same", text: a[i] });
      i++;
      j++;
    } else if (dp[i + 1][j] >= dp[i][j + 1]) {
      parts.push({ type: "del", text: a[i] });
      i++;
    } else {
      parts.push({ type: "add", text: b[j] });
      j++;
    }
  }
  while (i < n) {
    parts.push({ type: "del", text: a[i] });
    i++;
  }
  while (j < m) {
    parts.push({ type: "add", text: b[j] });
    j++;
  }

  return parts;
}
