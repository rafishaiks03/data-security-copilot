import {
  useEffect,
  useState,
  type ChangeEvent,
} from "react";
import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  Database,
  Filter,
  RefreshCw,
  Search,
  X,
} from "lucide-react";

import {
  getDataTable,
  getDataTables,
  type DataTableResponse,
} from "../api/client";

export default function DataExplorer() {
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState("");

  const [data, setData] =
    useState<DataTableResponse | null>(null);

  const [loadingTables, setLoadingTables] =
    useState(true);

  const [loadingData, setLoadingData] =
    useState(false);

  const [error, setError] = useState("");

  const [page, setPage] = useState(0);

  const pageSize = 25;

  const [searchInput, setSearchInput] =
    useState("");

  const [search, setSearch] = useState("");

  const [filterColumn, setFilterColumn] =
    useState("");

  const [filterValueInput, setFilterValueInput] =
    useState("");

  const [filterValue, setFilterValue] =
    useState("");

  const [filterMode, setFilterMode] = useState<
    "contains" | "equals"
  >("contains");

  const [sortBy, setSortBy] = useState("");

  const [sortOrder, setSortOrder] = useState<
    "asc" | "desc"
  >("asc");

  useEffect(() => {
    loadTables();
  }, []);

  useEffect(() => {
    if (selectedTable) {
      loadTable();
    }
  }, [
    selectedTable,
    page,
    search,
    filterColumn,
    filterValue,
    filterMode,
    sortBy,
    sortOrder,
  ]);

  async function loadTables() {
    try {
      setLoadingTables(true);
      setError("");

      const response = await getDataTables();

      setTables(response.tables);

      if (
        response.tables.length > 0 &&
        !selectedTable
      ) {
        setSelectedTable(response.tables[0]);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load database tables.",
      );
    } finally {
      setLoadingTables(false);
    }
  }

  async function loadTable() {
    try {
      setLoadingData(true);
      setError("");

      const response = await getDataTable(
        selectedTable,
        pageSize,
        page * pageSize,
        {
          search: search || undefined,
          filterColumn:
            filterColumn || undefined,
          filterValue:
            filterValue || undefined,
          filterMode,
          sortBy: sortBy || undefined,
          sortOrder,
        },
      );

      setData(response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load table data.",
      );
    } finally {
      setLoadingData(false);
    }
  }

  function handleTableChange(
    event: ChangeEvent<HTMLSelectElement>,
  ) {
    setSelectedTable(event.target.value);

    setPage(0);

    setSearchInput("");
    setSearch("");

    setFilterColumn("");
    setFilterValueInput("");
    setFilterValue("");

    setSortBy("");
    setSortOrder("asc");
  }

  function handleSearch() {
    setPage(0);
    setSearch(searchInput.trim());
  }

  function handleFilter() {
    if (
      filterValueInput.trim() &&
      !filterColumn
    ) {
      setError(
        "Select a filter column before applying a filter.",
      );
      return;
    }

    setError("");
    setPage(0);
    setFilterValue(filterValueInput.trim());
  }

  function clearFilters() {
    setSearchInput("");
    setSearch("");

    setFilterColumn("");
    setFilterValueInput("");
    setFilterValue("");

    setPage(0);
    setError("");
  }

  function handleSort(columnName: string) {
    setPage(0);

    if (sortBy === columnName) {
      setSortOrder((current) =>
        current === "asc" ? "desc" : "asc",
      );
      return;
    }

    setSortBy(columnName);
    setSortOrder("asc");
  }

  function handlePreviousPage() {
    setPage((current) =>
      Math.max(0, current - 1),
    );
  }

  function handleNextPage() {
    if (!data) {
      return;
    }

    if (
      data.offset + data.limit <
      data.count
    ) {
      setPage((current) => current + 1);
    }
  }

  const hasActiveFilters =
    Boolean(search || filterValue);

  const totalPages =
    data && data.count > 0
      ? Math.ceil(data.count / data.limit)
      : 0;

  const currentPage = page + 1;

  return (
    <div className="data-explorer-page">

      {/* Page heading */}
      <div className="data-explorer-header">
        <div>
          <div className="data-explorer-eyebrow">
            SECURITY DATA
          </div>

          <h1>Data Explorer</h1>

          <p>
            Explore database records and investigate
            security-related activity.
          </p>
        </div>

        <button
          type="button"
          className="data-refresh-button"
          onClick={() => {
            if (selectedTable) {
              loadTable();
            } else {
              loadTables();
            }
          }}
          disabled={
            loadingData || loadingTables
          }
        >
          <RefreshCw
            size={16}
            className={
              loadingData || loadingTables
                ? "spin"
                : ""
            }
          />

          Refresh
        </button>
      </div>

      {error && (
        <div className="data-explorer-error">
          {error}
        </div>
      )}

      {/* Database overview */}
      <div className="data-explorer-overview">

        <div className="database-card">

          <div className="database-icon">
            <Database size={21} />
          </div>

          <div className="database-card-content">

            <span className="database-label">
              DATABASE TABLE
            </span>

            <div className="database-name-row">

              <select
                value={selectedTable}
                onChange={handleTableChange}
                disabled={loadingTables}
              >
                {tables.map((table) => (
                  <option
                    key={table}
                    value={table}
                  >
                    {table}
                  </option>
                ))}
              </select>

              <span className="database-status">
                <span className="database-status-dot" />
                Connected
              </span>

            </div>

          </div>

        </div>

        <div className="database-stat">
          <span>RECORDS</span>

          <strong>
            {data
              ? data.count.toLocaleString()
              : "—"}
          </strong>
        </div>

        <div className="database-stat">
          <span>COLUMNS</span>

          <strong>
            {data
              ? data.columns.length
              : "—"}
          </strong>
        </div>

        <div className="database-stat">
          <span>PAGE</span>

          <strong>
            {data
              ? `${currentPage}${totalPages ? ` / ${totalPages}` : ""}`
              : "—"}
          </strong>
        </div>

      </div>

      {/* Search and filter panel */}
      <div className="explorer-control-panel">

        <div className="control-search-row">

          <div className="explorer-search">

            <Search size={17} />

            <input
              type="text"
              placeholder={`Search ${selectedTable || "table"}...`}
              value={searchInput}
              onChange={(event) =>
                setSearchInput(
                  event.target.value,
                )
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleSearch();
                }
              }}
            />

            {searchInput && (
              <button
                type="button"
                className="control-icon-button"
                onClick={() => {
                  setSearchInput("");
                  setSearch("");
                  setPage(0);
                }}
                title="Clear search"
              >
                <X size={15} />
              </button>
            )}

            <button
              type="button"
              className="search-button"
              onClick={handleSearch}
            >
              Search
            </button>

          </div>

        </div>

        <div className="control-filter-row">

          <div className="filter-title">
            <Filter size={15} />
            Filters
          </div>

          <select
            value={filterColumn}
            onChange={(event) => {
              setFilterColumn(
                event.target.value,
              );
              setPage(0);
            }}
          >
            <option value="">
              Column
            </option>

            {data?.columns.map(
              (column) => (
                <option
                  key={column.name}
                  value={column.name}
                >
                  {column.name}
                </option>
              ),
            )}
          </select>

          <select
            value={filterMode}
            onChange={(event) =>
              setFilterMode(
                event.target.value as
                  | "contains"
                  | "equals",
              )
            }
          >
            <option value="contains">
              Contains
            </option>

            <option value="equals">
              Equals
            </option>
          </select>

          <input
            type="text"
            placeholder="Value"
            value={filterValueInput}
            onChange={(event) =>
              setFilterValueInput(
                event.target.value,
              )
            }
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                handleFilter();
              }
            }}
          />

          <button
            type="button"
            className="apply-filter-button"
            onClick={handleFilter}
          >
            Apply Filter
          </button>

          {hasActiveFilters && (
            <button
              type="button"
              className="clear-button"
              onClick={clearFilters}
            >
              Clear
            </button>
          )}

        </div>

        {hasActiveFilters && (
          <div className="active-filter-bar">

            <span className="active-filter-label">
              Active filters
            </span>

            {search && (
              <span className="filter-chip">
                Search: {search}
              </span>
            )}

            {filterValue && (
              <span className="filter-chip">
                {filterColumn}{" "}
                {filterMode === "equals"
                  ? "="
                  : "contains"}{" "}
                {filterValue}
              </span>
            )}

          </div>
        )}

      </div>

      {/* Data grid */}
      <div className="data-grid-card">

        <div className="data-grid-header">

          <div>
            <span className="data-grid-title">
              {selectedTable || "Data"}
            </span>

            {data && (
              <span className="data-grid-subtitle">
                {data.count.toLocaleString()} records
              </span>
            )}
          </div>

          {loadingData && (
            <div className="table-loading">
              <RefreshCw
                size={14}
                className="spin"
              />
              Updating...
            </div>
          )}

        </div>

        <div className="data-table-wrapper">

          <table className="data-table">

            <thead>
              <tr>
                {data?.columns.map(
                  (column) => {

                    const isSorted =
                      sortBy === column.name;

                    return (
                      <th
                        key={column.name}
                        onClick={() =>
                          handleSort(
                            column.name,
                          )
                        }
                        className="sortable-column"
                      >
                        <div className="column-header">

                          <span>
                            {column.name}
                          </span>

                          {isSorted ? (
                            sortOrder ===
                            "asc" ? (
                              <ChevronUp
                                size={14}
                              />
                            ) : (
                              <ChevronDown
                                size={14}
                              />
                            )
                          ) : (
                            <ChevronDown
                              size={13}
                              className="sort-placeholder"
                            />
                          )}

                        </div>

                        <span className="column-type">
                          {column.type}
                        </span>
                      </th>
                    );
                  },
                )}
              </tr>
            </thead>

            <tbody>

              {data?.rows.length ? (
                data.rows.map(
                  (row, rowIndex) => (
                    <tr
                      key={rowIndex}
                    >
                      {data.columns.map(
                        (column) => (
                          <td
                            key={column.name}
                            title={formatCellValue(
                              row[
                                column.name
                              ],
                            )}
                          >
                            {formatTableCell(
                              column.name,
                              row[
                                column.name
                              ],
                            )}
                          </td>
                        ),
                      )}
                    </tr>
                  ),
                )
              ) : (
                <tr>
                  <td
                    colSpan={
                      data?.columns
                        .length || 1
                    }
                    className="data-table-empty"
                  >
                    {loadingData
                      ? "Loading records..."
                      : "No records found."}
                  </td>
                </tr>
              )}

            </tbody>

          </table>

        </div>

        {/* Pagination */}
        {data && (
          <div className="data-pagination">

            <div className="pagination-summary">
              Showing{" "}
              <strong>
                {data.count === 0
                  ? 0
                  : data.offset + 1}
              </strong>{" "}
              –{" "}
              <strong>
                {Math.min(
                  data.offset +
                    data.rows.length,
                  data.count,
                )}
              </strong>{" "}
              of{" "}
              <strong>
                {data.count.toLocaleString()}
              </strong>
            </div>

            <div className="pagination-controls">

              <button
                type="button"
                onClick={
                  handlePreviousPage
                }
                disabled={
                  page === 0 ||
                  loadingData
                }
              >
                <ChevronLeft size={15} />
              </button>

              <span>
                Page {currentPage}
                {totalPages
                  ? ` of ${totalPages}`
                  : ""}
              </span>

              <button
                type="button"
                onClick={
                  handleNextPage
                }
                disabled={
                  !data ||
                  data.offset +
                    data.limit >=
                    data.count ||
                  loadingData
                }
              >
                <ChevronRight size={15} />
              </button>

            </div>

          </div>
        )}

      </div>

    </div>
  );
}

function formatCellValue(
  value: unknown,
): string {
  if (
    value === null ||
    value === undefined
  ) {
    return "—";
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

function formatTableCell(
  columnName: string,
  value: unknown,
): React.ReactNode {
  if (
    value === null ||
    value === undefined
  ) {
    return (
      <span className="null-value">
        —
      </span>
    );
  }

  if (
    columnName === "known_fraud_label"
  ) {
    return (
      <span
        className={
          Number(value) === 1
            ? "fraud-badge fraud"
            : "fraud-badge clean"
        }
      >
        {Number(value) === 1
          ? "FRAUD"
          : "CLEAN"}
      </span>
    );
  }

  if (columnName === "status") {
    const status =
      String(value).toUpperCase();

    return (
      <span
        className={`status-badge status-${status.toLowerCase()}`}
      >
        {status}
      </span>
    );
  }

  if (columnName === "amount") {
    const numberValue =
      Number(value);

    if (!Number.isNaN(numberValue)) {
      return numberValue.toLocaleString(
        undefined,
        {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        },
      );
    }
  }

  if (
    columnName.endsWith("_id") ||
    columnName === "device_id"
  ) {
    const text = String(value);

    if (text.length > 18) {
      return (
        <span className="uuid-value">
          {text.slice(0, 8)}...
          {text.slice(-6)}
        </span>
      );
    }
  }

  if (
    columnName.includes("timestamp") ||
    columnName === "created_at"
  ) {
    const date =
      new Date(String(value));

    if (!Number.isNaN(date.getTime())) {
      return date.toLocaleString();
    }
  }

  return String(value);
}