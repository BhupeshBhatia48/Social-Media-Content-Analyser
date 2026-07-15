import { motion } from "framer-motion";
import ScoreCircle from "./ScoreCircle.jsx";

export default function OverallVerdict({ posts }) {
  const scored = posts.filter((p) => !p.skipped);
  if (scored.length === 0) return null;

  const avg = Math.round(
    scored.reduce((sum, p) => sum + p.engagement_score, 0) / scored.length
  );

  const counts = { positive: 0, neutral: 0, negative: 0 };
  scored.forEach((p) => {
    if (counts[p.sentiment] !== undefined) counts[p.sentiment]++;
  });
  const skippedCount = posts.length - scored.length;

  const headline =
    avg >= 66
      ? "Strong overall engagement potential"
      : avg >= 34
      ? "Moderate engagement potential — room to sharpen"
      : "Weak engagement potential across most posts";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="mb-6 flex items-center gap-5 rounded-xl2 border border-border-soft bg-surface-raised px-6 py-5 shadow-card"
    >
      <ScoreCircle score={avg} size={80} label="Overall" />
      <div>
        <p className="mb-1 text-[14px] font-medium text-ink">{headline}</p>
        <p className="text-[12.5px] text-ink-faint">
          {scored.length} post{scored.length === 1 ? "" : "s"} scored — {counts.positive}{" "}
          positive, {counts.neutral} neutral, {counts.negative} negative
          {skippedCount > 0 ? ` · ${skippedCount} skipped` : ""}
        </p>
      </div>
    </motion.div>
  );
}
