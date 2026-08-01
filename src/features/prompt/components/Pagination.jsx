import { memo } from "react";

function Pagination({ pagination, onPageChange, disabled }) {
  return (
    <nav className="pagination" aria-label="Insights pagination">
      <button
        type="button"
        className="secondary-button"
        onClick={() => onPageChange(pagination.page - 1)}
        disabled={disabled || pagination.page === 1}
      >
        Previous
      </button>
      <span>
        Page {pagination.page} of {pagination.totalPages} · {pagination.totalItems} insights
      </span>
      <button
        type="button"
        className="secondary-button"
        onClick={() => onPageChange(pagination.page + 1)}
        disabled={disabled || !pagination.hasNextPage}
      >
        Next
      </button>
    </nav>
  );
}

export default memo(Pagination);
