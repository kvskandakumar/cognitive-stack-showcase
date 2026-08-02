import { useCallback, useMemo, useState } from "react";
import { useGetInsightsQuery } from "../api/promptApi";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import InsightList from "./InsightList";
import InsightsToolbar from "./InsightsToolbar";
import Pagination from "./Pagination";

const searchableText = (insight) =>
  [insight.title, insight.content, ...Object.entries(insight.metadata || {}).flat()]
    .join(" ")
    .toLocaleLowerCase();

function SuccessResult({ requestId }) {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("title-asc");
  const debouncedSearch = useDebouncedValue(search.trim().toLocaleLowerCase());
  const { data, error, isLoading, isFetching, refetch } = useGetInsightsQuery({ requestId, page });

  const visibleInsights = useMemo(() => {
    const [field, direction] = sort.split("-");
    const filtered = (data?.insights || []).filter(
      (insight) => !debouncedSearch || searchableText(insight).includes(debouncedSearch),
    );

    return [...filtered].sort((first, second) => {
      const result = String(first[field] || "").localeCompare(String(second[field] || ""));
      return direction === "asc" ? result : -result;
    });
  }, [data?.insights, debouncedSearch, sort]);

  const changePage = useCallback((nextPage) => setPage(nextPage), []);

  if (isLoading) return <p className="empty-state" aria-live="polite">Loading insights…</p>;
  if (error) {
    return (
      <div className="result-card error-card" role="alert">
        <p>{error.data?.message || "Unable to load insights."}</p>
        <button type="button" onClick={refetch}>Try again</button>
      </div>
    );
  }

  return (
    <section aria-live="polite" aria-busy={isFetching}>
      <InsightsToolbar search={search} sort={sort} onSearchChange={setSearch} onSortChange={setSort} />
      {isFetching && <p className="loading-note">Updating results…</p>}
      <InsightList insights={visibleInsights} />
      {data?.pagination && <Pagination pagination={data.pagination} onPageChange={changePage} disabled={isFetching} />}
    </section>
  );
}

function PromptResult({ response }) {
  if (!response) return <p className="empty-state">Your AI response will appear here.</p>;
  if (response.status === "NEEDS_CLARIFICATION") {
    return <section className="result-card clarification-card"><h2>More information required</h2><p>{response.message}</p></section>;
  }
  if (response.status === "SUCCESS") return <SuccessResult key={response.requestId} requestId={response.requestId} />;
  return <div className="result-card error-card" role="alert">The server returned an unsupported response.</div>;
}

export default PromptResult;
