import { useEffect, useState } from "react";
import api from "../api/api";

import {
  ArcElement,
  Chart as ChartJS,
  Legend,
  Tooltip,
} from "chart.js";

import { Pie } from "react-chartjs-2";
import { EmptyState, ErrorState, SkeletonBlock } from "./DashboardStates";

ChartJS.register(ArcElement, Tooltip, Legend);

function SentimentPieChart({ uploadId }) {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      setIsLoading(true);
      setError("");

      const res = await api.get(
        uploadId ? `/analytics/dashboard/${uploadId}` : "/analytics/dashboard"
      );
      setData(res.data.sentiment_distribution || null);
    } catch (err) {
      console.log(err);
      setError("Unable to load sentiment distribution.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [uploadId]);

  const hasData = data && Object.values(data).some((value) => value > 0);

  return (
    <div className="bg-white p-6 rounded-xl shadow">
      <h2 className="text-xl font-bold mb-4">Sentiment Distribution</h2>

      {isLoading && (
        <div className="mx-auto h-72 max-w-md sm:h-80 lg:h-96">
          <SkeletonBlock className="h-full w-full rounded-full" />
        </div>
      )}

      {!isLoading && error && (
        <ErrorState message={error} onRetry={load} />
      )}

      {!isLoading && !error && !hasData && (
        <EmptyState
          title="No sentiment data yet"
          message="Upload reviews to see positive, negative, and neutral sentiment."
        />
      )}

      {!isLoading && !error && hasData && (
        <div className="mx-auto h-72 max-w-md sm:h-80 lg:h-96">
          <Pie
            data={{
              labels: Object.keys(data),
              datasets: [
                {
                  data: Object.values(data),
                  backgroundColor: ["#22c55e", "#ef4444", "#facc15"],
                  borderColor: "#ffffff",
                  borderWidth: 3,
                  hoverOffset: 8,
                },
              ],
            }}
            options={{
              animation: {
                duration: 650,
                easing: "easeOutQuart",
              },
              maintainAspectRatio: false,
              responsive: true,
              plugins: {
                legend: {
                  position: "bottom",
                  labels: {
                    boxWidth: 12,
                    boxHeight: 12,
                    color: "#475569",
                    padding: 18,
                    usePointStyle: true,
                  },
                },
              },
            }}
          />
        </div>
      )}
    </div>
  );
}

export default SentimentPieChart;
