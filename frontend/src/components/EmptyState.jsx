import { Sparkles } from "lucide-react";

export default function EmptyState() {
  return (
    <div className="mt-6 flex flex-col items-center gap-2 text-center">
      <div className="mb-1 flex h-9 w-9 items-center justify-center rounded-full bg-surface-raised">
        <Sparkles size={16} className="text-ink-faint" strokeWidth={1.6} />
      </div>
      <p className="max-w-sm text-[13px] leading-relaxed text-ink-faint">
        Upload a document above and each post inside it will be scored, summarized,
        and rewritten for stronger engagement.
      </p>
    </div>
  );
}
