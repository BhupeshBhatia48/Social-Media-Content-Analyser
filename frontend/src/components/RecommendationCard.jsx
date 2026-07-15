import { CheckCircle2, AlertTriangle } from "lucide-react";

export default function RecommendationCard({ type, text }) {
  const isStrength = type === "strength";
  return (
    <div className="flex items-start gap-2.5 rounded-lg bg-surface-raised/60 px-3 py-2.5">
      {isStrength ? (
        <CheckCircle2 size={15} className="mt-0.5 shrink-0 text-success" strokeWidth={2} />
      ) : (
        <AlertTriangle size={15} className="mt-0.5 shrink-0 text-warning" strokeWidth={2} />
      )}
      <p className="text-[13px] leading-snug text-ink-soft">{text}</p>
    </div>
  );
}
