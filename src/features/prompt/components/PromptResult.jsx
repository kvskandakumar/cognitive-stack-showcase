import { useSelector } from "react-redux";
import {
  selectPromptError,
  selectPromptResponse,
  selectPromptStatus,
} from "../store/promptSlice";
import StructuredError from "./StructuredError";

function SuccessResult({ response }) {
  const insights = Array.isArray(response.insights)
    ? response.insights
    : [];

  return (
    <section className="result-card success-card" aria-live="polite">
      <h2>AI insights</h2>

      {insights.length > 0 ? (
        <ul>
          {insights.map((insight, index) => (
            <li key={`${index}-${insight.slice(0, 30)}`}>
              {insight}
            </li>
          ))}
        </ul>
      ) : (
        <p>No insights were returned.</p>
      )}
    </section>
  );
}

function ClarificationResult({ response }) {
  return (
    <section className="result-card clarification-card" aria-live="polite">
      <h2>More information required</h2>

      <p>
        {response.message ||
          "Please provide more details so the request can be processed."}
      </p>
    </section>
  );
}

function PromptResult() {
  const status = useSelector(selectPromptStatus);
  const response = useSelector(selectPromptResponse);
  const error = useSelector(selectPromptError);

  if (status === "idle") {
    return (
      <section className="empty-state">
        <p>Your AI response will appear here.</p>
      </section>
    );
  }

  if (status === "loading") {
    return (
      <section className="result-card" aria-live="polite">
        <p>Processing your request...</p>
      </section>
    );
  }

  if (status === "failed") {
    return <StructuredError error={error} />;
  }

  if (!response) {
    return null;
  }

  switch (response.status) {
    case "SUCCESS":
      return <SuccessResult response={response} />;

    case "NEEDS_CLARIFICATION":
      return <ClarificationResult response={response} />;

    default:
      return (
        <StructuredError
          error={{
            message: "The server returned an unsupported response.",
            errors: [],
          }}
        />
      );
  }
}

export default PromptResult;