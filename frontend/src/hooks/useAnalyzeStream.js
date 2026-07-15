import { useCallback, useRef, useState } from "react";

/**
 * Encapsulates the exact same SSE parsing logic as before — only the
 * rendering layer changed. Talks to the same /api/analyze endpoint,
 * same event names (extraction, post_count, post, done, error).
 */
export function useAnalyzeStream() {
  const [status, setStatus] = useState("idle"); // idle | uploading | streaming | done | error
  const [statusText, setStatusText] = useState("");
  const [errorMessage, setErrorMessage] = useState(null);
  const [extraction, setExtraction] = useState(null);
  const [posts, setPosts] = useState([]);
  const [expectedCount, setExpectedCount] = useState(0);

  const reset = useCallback(() => {
    setStatus("idle");
    setStatusText("");
    setErrorMessage(null);
    setExtraction(null);
    setPosts([]);
    setExpectedCount(0);
  }, []);

  const analyzeFile = useCallback(async (file) => {
    reset();
    setStatus("uploading");
    setStatusText("Uploading file…");

    const formData = new FormData();
    formData.append("file", file);

    let response;
    try {
      response = await fetch("/api/analyze", { method: "POST", body: formData });
    } catch (err) {
      setStatus("error");
      setErrorMessage("Could not reach the server. Check your connection and try again.");
      return;
    }

    if (!response.ok) {
      let detail = "Something went wrong processing this file.";
      try {
        const body = await response.json();
        detail = body.error || detail;
      } catch (_) {
        /* ignore parse failure, use default message */
      }
      setStatus("error");
      setErrorMessage(detail);
      return;
    }

    setStatus("streaming");
    setStatusText("Extracting text…");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let received = 0;
    let expected = 0;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const events = buffer.split("\n\n");
      buffer = events.pop();

      for (const rawEvent of events) {
        if (!rawEvent.trim()) continue;
        const lines = rawEvent.split("\n");
        let eventName = "message";
        let dataStr = "";
        for (const line of lines) {
          if (line.startsWith("event:")) eventName = line.slice(6).trim();
          if (line.startsWith("data:")) dataStr += line.slice(5).trim();
        }
        if (!dataStr) continue;

        let data;
        try {
          data = JSON.parse(dataStr);
        } catch (_) {
          continue;
        }

        if (eventName === "error") {
          setStatus("error");
          setErrorMessage(data.error);
          return;
        }
        if (eventName === "extraction") {
          setExtraction(data);
          setStatusText("Analyzing posts…");
        }
        if (eventName === "post_count") {
          expected = data.count;
          setExpectedCount(expected);
        }
        if (eventName === "post") {
          received += 1;
          setPosts((prev) => [...prev, data]);
          setStatusText(
            expected ? `Analyzing posts… (${received}/${expected})` : "Analyzing posts…"
          );
        }
        if (eventName === "done") {
          setStatus("done");
        }
      }
    }
  }, [reset]);

  return {
    status,
    statusText,
    errorMessage,
    extraction,
    posts,
    expectedCount,
    analyzeFile,
    reset,
  };
}
