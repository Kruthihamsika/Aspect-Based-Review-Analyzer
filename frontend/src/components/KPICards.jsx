import { useEffect, useState } from "react";
import api from "../api/api";
import { ErrorState, SkeletonBlock } from "./DashboardStates";

function KPICards({ uploadId }) {
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      setIsLoading(true);
      setError("");

      const res = await api.get(
        uploadId ? `/analytics/dashboard/${uploadId}` : "/analytics/dashboard"
      );
      setSummary(res.data.summary);
    } catch (err) {
      console.error("Error:", err);
      setError("Unable to load dashboard summary.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [uploadId]);

  if (isLoading) {
    return (
      <div className="mt-8 grid grid-cols-5 gap-5">
        {[1, 2, 3, 4, 5].map((item) => (
          <div key={item} className="rounded-xl bg-white p-6 shadow">
            <SkeletonBlock className="h-4 w-20" />
            <SkeletonBlock className="mt-5 h-9 w-24" />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-8">
        <ErrorState message={error} onRetry={load} />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-5 gap-5 mt-8">
      <div className="bg-blue-500 text-white p-6 rounded-xl">
        <h2>Reviews</h2>
        <h1 className="text-3xl font-bold">{summary.total_reviews}</h1>
      </div>

      <div className="bg-purple-500 text-white p-6 rounded-xl">
        <h2>Aspects</h2>
        <h1 className="text-3xl font-bold">{summary.total_aspects}</h1>
      </div>

      <div className="bg-green-500 text-white p-6 rounded-xl">
        <h2>Positive</h2>
        <h1 className="text-3xl font-bold">{summary.positive}</h1>
      </div>

      <div className="bg-red-500 text-white p-6 rounded-xl">
        <h2>Negative</h2>
        <h1 className="text-3xl font-bold">{summary.negative}</h1>
      </div>

      <div className="bg-yellow-500 text-white p-6 rounded-xl">
        <h2>Neutral</h2>
        <h1 className="text-3xl font-bold">{summary.neutral}</h1>
      </div>
    </div>
  );
}

export default KPICards;
