import { useState } from "react";
import PromptForm from "../components/PromptForm";
import PromptResult from "../components/PromptResult";

function PromptPage() {
  const [response, setResponse] = useState(null);
  return (
    <main className="page-container">
      <header className="page-header">
        <p className="eyebrow">AI Middleware Client</p>
        <h1>Generate AI insights</h1>
        <p>
          Submit a detailed prompt and select the language in which the
          response should be generated.
        </p>
      </header>

      <div className="content-grid">
        <section className="panel">
          <h2>Request</h2>
          <PromptForm onResult={setResponse} />
        </section>

        <section className="panel">
          <h2>Response</h2>
          <PromptResult response={response} />
        </section>
      </div>
    </main>
  );
}

export default PromptPage;
