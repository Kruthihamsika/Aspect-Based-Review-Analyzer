import {
  AlertCircle,
  BarChart3,
  Calendar,
  Database,
  FileText,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import UploadCard from "../components/UploadCard";

function DatasetLibrary() {
  const navigate = useNavigate();
  const [datasets, setDatasets] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDatasets = async () => {
    try {
      setIsLoading(true);
      setError("");

      const response = await api.get("/uploads");
      setDatasets(response.data || []);
    } catch (err) {
      console.error(err);
      setError("Unable to load uploaded datasets.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDatasets();
  }, []);

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
                Dataset Library
              </p>

              <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl lg:text-5xl">
                Aspect-Based Review Analyzer
              </h1>

              <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
                Upload review CSVs and open a separate analytics dashboard for each dataset.
              </p>
            </div>

            <button
              type="button"
              onClick={loadDatasets}
              className="inline-flex w-fit items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50"
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>
        </div>
      </div>

      <main className="mx-auto max-w-7xl px-5 py-6 sm:px-8 sm:py-8 lg:px-10 lg:py-10">
        <UploadCard onUploadSuccess={loadDatasets} />

        <section className="rounded-xl bg-white p-8 shadow">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-sky-700">
                Uploaded CSVs
              </p>

              <h2 className="mt-2 text-2xl font-bold text-slate-950">
                Datasets
              </h2>
            </div>

            <div className="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-600">
              {datasets.length} datasets
            </div>
          </div>

          {isLoading && (
            <div className="mt-6 flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-5 text-slate-600">
              <Loader2 className="animate-spin text-blue-600" size={20} />
              <span className="font-semibold">Loading datasets...</span>
            </div>
          )}

          {!isLoading && error && (
            <div className="mt-6 flex flex-col gap-4 rounded-xl border border-rose-200 bg-rose-50 p-5 text-rose-800 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-start gap-3">
                <AlertCircle className="mt-0.5 shrink-0" size={20} />
                <p className="font-semibold">{error}</p>
              </div>

              <button
                type="button"
                onClick={loadDatasets}
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700"
              >
                <RefreshCw size={15} />
                Retry
              </button>
            </div>
          )}

          {!isLoading && !error && datasets.length === 0 && (
            <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-8 text-center">
              <Database className="mx-auto text-slate-400" size={36} />
              <h3 className="mt-4 text-lg font-bold text-slate-950">
                No datasets uploaded yet
              </h3>
              <p className="mt-2 text-slate-600">
                Upload a CSV to create its own analytics dashboard.
              </p>
            </div>
          )}

          {!isLoading && !error && datasets.length > 0 && (
            <div className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
              {datasets.map((dataset) => (
                <DatasetCard
                  key={dataset.id}
                  dataset={dataset}
                  onOpen={() => navigate(`/dashboard/${dataset.id}`)}
                />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function DatasetCard({ dataset, onOpen }) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-sky-100 bg-sky-50 text-sky-700">
          <FileText size={22} />
        </div>

        <div className="min-w-0 flex-1">
          <h3 className="truncate text-lg font-bold text-slate-950">
            {dataset.filename}
          </h3>

          <p className="mt-1 text-sm font-semibold text-slate-500">
            {dataset.total_reviews || 0} reviews
          </p>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-1 gap-3 text-sm text-slate-600">
        <div className="flex items-center gap-2">
          <Calendar className="text-slate-400" size={16} />
          <span>{formatUploadDate(dataset.created_at)}</span>
        </div>

        <div className="flex items-center gap-2">
          <Database className="text-slate-400" size={16} />
          <span className="capitalize">{dataset.status || "Unknown"}</span>
        </div>
      </div>

      <button
        type="button"
        onClick={onOpen}
        className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
      >
        <BarChart3 size={18} />
        Open Dashboard
      </button>
    </article>
  );
}

function formatUploadDate(value) {
  if (!value) {
    return "Upload date unavailable";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default DatasetLibrary;
