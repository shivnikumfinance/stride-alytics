import { classNames } from "../../utils";

interface Column<T> {
  key: string;
  header: string;
  align?: "left" | "right" | "center";
  render: (row: T) => React.ReactNode;
  className?: string;
}

interface TableProps<T> {
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T) => string;
  empty?: React.ReactNode;
  loading?: boolean;
  className?: string;
}

export function Table<T>({ columns, rows, rowKey, empty, loading, className }: TableProps<T>) {
  if (loading) {
    return <div className="p-8 text-center text-sm text-gray-500">Loading…</div>;
  }
  if (rows.length === 0) {
    return <div className="p-8 text-center text-sm text-gray-500">{empty ?? "No data"}</div>;
  }
  return (
    <div className={classNames("overflow-x-auto rounded-lg border border-gray-200 bg-white", className)}>
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          <tr>
            {columns.map((c) => (
              <th
                key={c.key}
                scope="col"
                className={classNames(
                  "px-4 py-3",
                  c.align === "right" && "text-right",
                  c.align === "center" && "text-center",
                  c.className,
                )}
              >
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {rows.map((row) => (
            <tr key={rowKey(row)} className="hover:bg-gray-50">
              {columns.map((c) => (
                <td
                  key={c.key}
                  className={classNames(
                    "px-4 py-3 whitespace-nowrap",
                    c.align === "right" && "text-right",
                    c.align === "center" && "text-center",
                    c.className,
                  )}
                >
                  {c.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
