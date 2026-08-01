function StructuredError({ error }) {
  if (!error) {
    return null;
  }

  return (
    <section className="result-card error-card" role="alert">
      <h2>Request failed</h2>

      <p>{error.message}</p>

      {error.statusCode && (
        <p className="status-code">
          Status code: {error.statusCode}
        </p>
      )}

      {Array.isArray(error.errors) && error.errors.length > 0 && (
        <ul>
          {error.errors.map((item, index) => (
            <li key={`${item.field || "error"}-${index}`}>
              {item.field && <strong>{item.field}: </strong>}
              {item.message}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default StructuredError;