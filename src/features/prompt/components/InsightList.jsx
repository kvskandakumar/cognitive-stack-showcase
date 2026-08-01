import { memo } from "react";

const InsightRow = memo(function InsightRow({ insight }) {
  return (
    <article className="insight-row">
      <div>
        <h3>{insight.title}</h3>
        <p>{insight.content}</p>
      </div>
      <dl className="insight-metadata">
        {Object.entries(insight.metadata || {}).map(([key, value]) => (
          <div key={key}>
            <dt>{key}</dt>
            <dd>{String(value)}</dd>
          </div>
        ))}
      </dl>
    </article>
  );
});

function InsightList({ insights }) {
  if (!insights.length) {
    return <p className="empty-state">No insights match your search.</p>;
  }

  return (
    <div className="insight-list">
      {insights.map((insight) => (
        <InsightRow key={insight.id} insight={insight} />
      ))}
    </div>
  );
}

export default memo(InsightList);
