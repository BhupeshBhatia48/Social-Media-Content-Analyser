import { motion } from "framer-motion";
import { FileText, ScanLine } from "lucide-react";

export default function ExtractionLog({ pages }) {
  if (!pages?.length) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.25 }}
      className="mb-6 flex flex-wrap gap-2"
    >
      {pages.map((page) => {
        const isOcr = page.method === "ocr";
        return (
          <div
            key={page.page_number}
            className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px]
              ${isOcr
                ? "border-warning/25 bg-warning-soft text-warning"
                : "border-info/25 bg-info-soft text-info"}`}
          >
            {isOcr ? <ScanLine size={11} /> : <FileText size={11} />}
            <span>
              Page {page.page_number} · {isOcr ? `OCR ${page.ocr_confidence}%` : "text"}
            </span>
          </div>
        );
      })}
    </motion.div>
  );
}
