import { memo } from "react";

function InsightsToolbar({ search, sort, onSearchChange, onSortChange }) {
  return (
    <div className="insights-toolbar">
      <div className="form-group">
        <label htmlFor="insight-search">Search this page</label>
        <input
          id="insight-search"
          type="search"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Search text or metadata…"
        />
      </div>
      <div className="form-group sort-control">
        <label htmlFor="insight-sort">Sort</label>
        <select
          id="insight-sort"
          value={sort}
          onChange={(event) => onSortChange(event.target.value)}
        >
          <option value="title-asc">Title: A–Z</option>
          <option value="title-desc">Title: Z–A</option>
          <option value="content-asc">Content: A–Z</option>
          <option value="content-desc">Content: Z–A</option>
        </select>
      </div>
    </div>
  );
}

export default memo(InsightsToolbar);
