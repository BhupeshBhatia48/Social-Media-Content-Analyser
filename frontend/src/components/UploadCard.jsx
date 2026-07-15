import { useRef, useState } from "react";
import { motion } from "framer-motion";
import { UploadCloud, FileText } from "lucide-react";

export default function UploadCard({ onFileSelected, disabled }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = (files) => {
    const file = files?.[0];
    if (file) onFileSelected(file);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        if (!disabled) handleFiles(e.dataTransfer.files);
      }}
      onClick={() => !disabled && inputRef.current?.click()}
      role="button"
      tabIndex={0}
      aria-label="Upload a PDF or image file"
      onKeyDown={(e) => {
        if ((e.key === "Enter" || e.key === " ") && !disabled) {
          e.preventDefault();
          inputRef.current?.click();
        }
      }}
      className={`group relative flex cursor-pointer flex-col items-center justify-center rounded-xl2 border px-8 py-14 text-center transition-all duration-200
        ${isDragging
          ? "border-accent/60 bg-accent-soft"
          : "border-border bg-surface hover:border-border-soft hover:bg-surface-raised"}
        ${disabled ? "pointer-events-none opacity-60" : ""}
      `}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,.webp"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />

      <div
        className={`mb-4 flex h-12 w-12 items-center justify-center rounded-full transition-colors
          ${isDragging ? "bg-accent/20" : "bg-surface-raised group-hover:bg-accent-soft"}`}
      >
        {isDragging ? (
          <FileText size={22} className="text-accent" strokeWidth={1.6} />
        ) : (
          <UploadCloud size={22} className="text-ink-soft group-hover:text-accent" strokeWidth={1.6} />
        )}
      </div>

      <p className="mb-1 text-[15px] font-medium text-ink">
        {isDragging ? "Drop it here" : "Drop a document to analyze"}
      </p>
      <p className="text-[13px] text-ink-faint">
        PDF, PNG, JPG, or WEBP · up to 15MB
      </p>
    </motion.div>
  );
}
