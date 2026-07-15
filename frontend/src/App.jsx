import { AnimatePresence } from "framer-motion";
import Navbar from "./components/Navbar.jsx";
import UploadCard from "./components/UploadCard.jsx";
import EmptyState from "./components/EmptyState.jsx";
import LoadingSkeleton from "./components/LoadingSkeleton.jsx";
import Toast from "./components/Toast.jsx";
import ExtractionLog from "./components/ExtractionLog.jsx";
import OverallVerdict from "./components/OverallVerdict.jsx";
import AnalysisCard from "./components/AnalysisCard.jsx";
import Footer from "./components/Footer.jsx";
import { useAnalyzeStream } from "./hooks/useAnalyzeStream.js";

export default function App() {
  const {
    status,
    statusText,
    errorMessage,
    extraction,
    posts,
    expectedCount,
    analyzeFile,
    reset,
  } = useAnalyzeStream();

  const isBusy = status === "uploading" || status === "streaming";
  const pendingSkeletons = Math.max(expectedCount - posts.length, 0);

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />

      <main className="mx-auto max-w-3xl px-6 py-10">
        <UploadCard onFileSelected={analyzeFile} disabled={isBusy} />

        {isBusy && (
          <p className="mt-4 text-center text-[12.5px] text-ink-faint">{statusText}</p>
        )}

        <div className="mt-8">
          <Toast message={errorMessage} onDismiss={reset} />
        </div>

        {status === "idle" && !errorMessage && <EmptyState />}

        {extraction && <ExtractionLog pages={extraction.pages} />}

        {status === "done" && <OverallVerdict posts={posts} />}

        <div className="space-y-4">
          <AnimatePresence>
            {posts.map((post) => (
              <AnalysisCard key={post.post_index} post={post} index={post.post_index} />
            ))}
            {isBusy &&
              extraction &&
              Array.from({ length: Math.min(pendingSkeletons, 3) }).map((_, i) => (
                <LoadingSkeleton key={`skeleton-${i}`} />
              ))}
          </AnimatePresence>
        </div>
      </main>

      <Footer />
    </div>
  );
}
