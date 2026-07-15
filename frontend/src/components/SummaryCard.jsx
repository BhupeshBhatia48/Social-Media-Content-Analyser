import { Sparkles } from "lucide-react";

export default function SummaryCard({ text }) {
  return (
    <div className="flex items-start gap-2.5 rounded-lg bg-accent-soft px-3.5 py-3">
      <Sparkles size={15} className="mt-0.5 shrink-0 text-accent" strokeWidth={2} />
      <p className="text-[13.5px] leading-relaxed text-ink">{text}</p>
    </div>
  );
}
