import { motion } from "framer-motion";
import { FileWarning } from "lucide-react";
import ScoreCircle from "./ScoreCircle.jsx";
import SummaryCard from "./SummaryCard.jsx";
import MetricCard from "./MetricCard.jsx";
import RecommendationCard from "./RecommendationCard.jsx";
import Accordion from "./Accordion.jsx";
import { diffWords } from "../utils/diff.js";

function DiffMarkup({ original, improved }) {
  const parts = diffWords(original, improved);
  return (
    <p className="whitespace-pre-wrap font-mono text-[12.5px] leading-relaxed text-ink-soft">
      {parts.map((p, idx) => {
        if (p.type === "same") return <span key={idx}>{p.text}</span>;
        if (p.type === "del")
          return (
            <span key={idx} className="text-danger line-through decoration-[1.5px] opacity-70">
              {p.text}
            </span>
          );
        return (
          <span key={idx} className="font-medium text-success underline decoration-[1.5px]">
            {p.text}
          </span>
        );
      })}
    </p>
  );
}

export default function AnalysisCard({ post, index }) {
  if (post.skipped) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="rounded-xl2 border border-border-soft bg-surface p-6"
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="mb-1 text-[13px] font-medium text-ink-faint">Post {index + 1}</p>
            <div className="flex items-center gap-2">
              <FileWarning size={14} className="text-warning" />
              <span className="text-[13px] text-ink-soft">{post.skip_reason || "Skipped"}</span>
            </div>
          </div>
        </div>
        <div className="mt-4 rounded-lg bg-surface-raised/60 px-3.5 py-3">
          <p className="whitespace-pre-wrap text-[13px] leading-relaxed text-ink-faint">
            {post.original_text}
          </p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="rounded-xl2 border border-border-soft bg-surface p-6 shadow-card"
    >
      {/* Header: title + score */}
      <div className="mb-4 flex items-start justify-between gap-4">
        <p className="pt-1 text-[13px] font-medium text-ink-faint">Post {index + 1}</p>
        <ScoreCircle score={post.engagement_score} size={72} />
      </div>

      {/* AI summary — hero element */}
      <div className="mb-4">
        <SummaryCard text={post.engagement_justification} />
      </div>

      {/* Metrics */}
      <div className="mb-5 grid grid-cols-2 gap-2">
        <MetricCard label="Sentiment" value={post.sentiment} />
      </div>

      {/* Recommendations */}
      <div className="mb-1 grid grid-cols-1 gap-2 sm:grid-cols-2">
        <div className="space-y-1.5">
          {(post.strengths || []).map((s, i) => (
            <RecommendationCard key={`s-${i}`} type="strength" text={s} />
          ))}
        </div>
        <div className="space-y-1.5">
          {(post.weaknesses || []).map((w, i) => (
            <RecommendationCard key={`w-${i}`} type="weakness" text={w} />
          ))}
        </div>
      </div>

      {/* Improved version */}
      <div className="mt-5 rounded-lg bg-surface-raised/60 px-3.5 py-3">
        <p className="mb-1.5 text-[11px] uppercase tracking-wide text-ink-faint">
          Improved version
        </p>
        <p className="whitespace-pre-wrap text-[13.5px] leading-relaxed text-ink">
          {post.improved_version}
        </p>
      </div>

      {/* Original content — collapsed by default */}
      <div className="mt-4">
        <Accordion title="View original post">
          <p className="whitespace-pre-wrap text-[13px] leading-relaxed text-ink-faint">
            {post.original_text}
          </p>
        </Accordion>
      </div>

      {/* Detailed word-level diff — collapsed by default */}
      <div className="mt-1">
        <Accordion title="View detailed changes">
          <DiffMarkup original={post.original_text} improved={post.improved_version} />
        </Accordion>
      </div>
    </motion.div>
  );
}
