import { useState } from "react";
import { ArrowLeft } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import UploadCard from "../components/UploadCard";
import KPICards from "../components/KPICards";
import AspectBarChart from "../components/AspectBarChart";
import SentimentPieChart from "../components/SentimentPieChart";
import TopPositiveChart from "../components/TopPositiveChart";
import TopNegativeChart from "../components/TopNegativeChart";
import BusinessInsights from "../components/BusinessInsights";
import SearchAspect from "../components/SearchAspect";

function Dashboard() {
  const navigate = useNavigate();
  const { uploadId } = useParams();
  const [refreshKey, setRefreshKey] = useState(0);

  const refreshDashboard = () => {
    setRefreshKey((currentKey) => currentKey + 1);
    navigate("/");
  };

  return (
    <div className="dashboard-shell min-h-screen bg-slate-50 text-slate-900">

      <div className="relative overflow-hidden border-b border-slate-200 bg-white">
        <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-sky-500 via-indigo-500 to-emerald-400" />
        <div className="absolute -right-24 -top-32 h-72 w-72 rounded-full bg-sky-100 blur-3xl" />
        <div className="absolute -left-24 top-10 h-64 w-64 rounded-full bg-emerald-100 blur-3xl" />

        <div className="relative mx-auto flex max-w-7xl flex-col gap-5 px-5 py-8 sm:px-8 lg:px-10">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-sky-700">
                Sentiment Analytics
              </p>

              <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl lg:text-5xl">
                Aspect-Based Review Analyzer
              </h1>

              <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
                AI powered aspect level sentiment analysis dashboard.
              </p>
            </div>

            <button
              type="button"
              onClick={() => navigate("/")}
              className="inline-flex w-fit items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50"
            >
              <ArrowLeft size={16} />
              Dataset Library
            </button>
          </div>
        </div>
      </div>

      <main className="mx-auto max-w-7xl px-5 py-6 sm:px-8 sm:py-8 lg:px-10 lg:py-10">

        <UploadCard onUploadSuccess={refreshDashboard} />

        <div key={refreshKey} className="dashboard-content">
          <KPICards uploadId={uploadId} />

          <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
            <AspectBarChart uploadId={uploadId} />
            <SentimentPieChart uploadId={uploadId} />
          </div>

          <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
            <TopPositiveChart uploadId={uploadId} />
            <TopNegativeChart uploadId={uploadId} />
          </div>

          <div className="mt-6">
            <BusinessInsights uploadId={uploadId} />
          </div>

          <div className="mt-6 mb-10">
            <SearchAspect uploadId={uploadId} />
          </div>
        </div>

      </main>
    </div>
  );
}

export default Dashboard;
