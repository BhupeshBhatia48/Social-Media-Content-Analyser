import { FileSearch } from "lucide-react";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-10 border-b border-border-soft bg-canvas/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-accent-soft">
            <FileSearch size={15} className="text-accent" strokeWidth={2} />
          </div>
          <span className="text-[14.5px] font-medium text-ink">Content Analyzer</span>
        </div>
        <span className="text-[12px] text-ink-faint">Post-level engagement analysis</span>
      </div>
    </header>
  );
}
