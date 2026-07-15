import { motion } from "framer-motion";

const TIER_COLORS = {
  high: { stroke: "#3DD68C", text: "text-success" },
  mid: { stroke: "#F0B054", text: "text-warning" },
  low: { stroke: "#F0616E", text: "text-danger" },
};

function tierFor(score) {
  if (score >= 66) return "high";
  if (score >= 34) return "mid";
  return "low";
}

/**
 * Large animated circular score indicator. The stroke draws in from 0
 * to the score value on mount — the one deliberate "hero" animation
 * per card, everything else stays subtle.
 */
export default function ScoreCircle({ score, size = 88, label = "Engagement" }) {
  const tier = tierFor(score);
  const colors = TIER_COLORS[tier];
  const radius = (size - 10) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-1.5">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#26272C"
            strokeWidth="6"
          />
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={colors.stroke}
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1], delay: 0.1 }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-xl font-semibold ${colors.text}`}>{score}</span>
        </div>
      </div>
      <span className="text-[11px] uppercase tracking-wide text-ink-faint">{label}</span>
    </div>
  );
}
