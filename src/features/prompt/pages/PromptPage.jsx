import PromptForm from "../components/PromptForm";
// import PromptResult from "../components/PromptResult";

function PromptPage() {
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
          <PromptForm />
        </section>

        <section className="panel">
          <h2>Response</h2>
          {/* <PromptResult /> */}
        </section>
      </div>
    </main>
  );
}

export default PromptPage;