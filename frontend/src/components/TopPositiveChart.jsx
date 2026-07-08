import { useEffect, useState } from "react";
import api from "../api/api";
import { EmptyState, ErrorState, SkeletonBlock } from "./DashboardStates";

function TopPositiveChart({ uploadId }) {
  const [rows, setRows] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      setIsLoading(true);
      setError("");

      const res = await api.get(
        uploadId ? `/analytics/dashboard/${uploadId}` : "/analytics/dashboard"
      );
      setRows(res.data.top_positive_aspects || []);
    } catch (err) {
      console.log(err);
      setError("Unable to load positive aspects.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [uploadId]);

  return (
    <div className="bg-white p-6 rounded-xl shadow">
      <h2 className="text-xl font-bold mb-4">Top Positive Aspects</h2>

      {isLoading && <TableSkeleton />}

      {!isLoading && error && (
        <ErrorState message={error} onRetry={load} />
      )}

      {!isLoading && !error && !rows.length && (
        <EmptyState
          title="No positive aspects yet"
          message="Positive aspect trends will appear after reviews are analyzed."
        />
      )}

      {!isLoading && !error && rows.length > 0 && (
        <table className="w-full animate-fade-in">
          <thead>
            <tr>
              <th className="text-left">Aspect</th>
              <th>Positive %</th>
            </tr>
          </thead>

          <tbody>
            {rows.map((row) => (
              <tr key={row.aspect}>
                <td>{row.aspect}</td>
                <td className="text-green-600 font-bold">
                  {row.positive_percentage}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function TableSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3, 4, 5].map((item) => (
        <div key={item} className="flex items-center justify-between gap-4">
          <SkeletonBlock className="h-4 w-40" />
          <SkeletonBlock className="h-4 w-16" />
        </div>
      ))}
    </div>
  );
}

export default TopPositiveChart;
