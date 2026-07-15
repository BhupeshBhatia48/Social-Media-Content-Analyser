import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle, X } from "lucide-react";

export default function Toast({ message, onDismiss }) {
  return (
    <AnimatePresence>
      {message && (
        <motion.div
          initial={{ opacity: 0, y: -8, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -8, scale: 0.98 }}
          transition={{ duration: 0.2 }}
          className="mb-6 flex items-start gap-3 rounded-xl border border-danger/25 bg-danger-soft px-4 py-3.5"
        >
          <AlertCircle size={16} className="mt-0.5 shrink-0 text-danger" strokeWidth={2} />
          <p className="flex-1 text-[13px] leading-relaxed text-ink">{message}</p>
          <button
            onClick={onDismiss}
            aria-label="Dismiss"
            className="shrink-0 rounded-md p-0.5 text-ink-faint transition-colors hover:text-ink"
          >
            <X size={14} />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
