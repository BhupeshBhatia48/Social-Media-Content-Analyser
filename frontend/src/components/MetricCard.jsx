const SENTIMENT_STYLES = {
  positive: { dot: "bg-success", text: "text-success" },
  neutral: { dot: "bg-info", text: "text-info" },
  negative: { dot: "bg-danger", text: "text-danger" },
};

export default function MetricCard({ label, value }) {
  const style = SENTIMENT_STYLES[value] || { dot: "bg-ink-faint", text: "text-ink-soft" };
  return (
    <div className="flex items-center gap-2 rounded-lg border border-border-soft bg-surface-raised/50 px-3 py-2">
      <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
      <span className="text-[11px] uppercase tracking-wide text-ink-faint">{label}</span>
      <span className={`ml-auto text-[12.5px] font-medium capitalize ${style.text}`}>{value}</span>
    </div>
  );
}
