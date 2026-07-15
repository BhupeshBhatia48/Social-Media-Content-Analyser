import { motion } from "framer-motion";

function Bar({ className = "" }) {
  return (
    <div className={`animate-pulse rounded-md bg-surface-raised ${className}`} />
  );
}

export default function LoadingSkeleton() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="rounded-xl2 border border-border-soft bg-surface p-6"
    >
      <div className="mb-5 flex items-center justify-between">
        <Bar className="h-4 w-32" />
        <Bar className="h-11 w-11 rounded-full" />
      </div>
      <Bar className="mb-2 h-3 w-full" />
      <Bar className="mb-5 h-3 w-4/5" />
      <div className="flex gap-2">
        <Bar className="h-6 w-20 rounded-full" />
        <Bar className="h-6 w-24 rounded-full" />
      </div>
    </motion.div>
  );
}
