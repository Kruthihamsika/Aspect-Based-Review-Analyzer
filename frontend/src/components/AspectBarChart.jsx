import { useEffect, useState } from "react";
import api from "../api/api";
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { EmptyState, ErrorState, SkeletonBlock } from "./DashboardStates";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

function AspectBarChart({ uploadId }) {
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      setIsLoading(true);
      setError("");

      const res = await api.get(
        uploadId ? `/analytics/dashboard/${uploadId}` : "/analytics/dashboard"
      );
      setData(res.data.top_mentioned_aspects || []);
    } catch (err) {
      console.log(err);
      setError("Unable to load aspect mentions.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [uploadId]);

  return (
    <div className="bg-white p-6 rounded-xl shadow">
      <h2 className="text-xl font-bold mb-4">Top Mentioned Aspects</h2>

      {isLoading && (
        <div className="h-72 sm:h-80 lg:h-96">
          <SkeletonBlock className="h-full w-full" />
        </div>
      )}

      {!isLoading && error && (
        <ErrorState message={error} onRetry={load} />
      )}

      {!isLoading && !error && !data.length && (
        <EmptyState
          title="No aspect mentions yet"
          message="Upload and analyze reviews to see the most mentioned aspects."
        />
      )}

      {!isLoading && !error && data.length > 0 && (
        <div className="h-72 sm:h-80 lg:h-96">
          <Bar
            data={{
              labels: data.map((a) => a.aspect),
              datasets: [
                {
                  label: "Mentions",
                  data: data.map((a) => a.count),
                  backgroundColor: "#2563eb",
                  borderRadius: 8,
                  maxBarThickness: 46,
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
                  display: false,
                },
              },
              scales: {
                x: {
                  ticks: {
                    color: "#64748b",
                    maxRotation: 35,
                    minRotation: 0,
                  },
                  grid: {
                    display: false,
                  },
                },
                y: {
                  beginAtZero: true,
                  ticks: {
                    color: "#64748b",
                    precision: 0,
                  },
                  grid: {
                    color: "#e2e8f0",
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

export default AspectBarChart;
