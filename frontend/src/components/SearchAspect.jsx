import { AlertCircle, Loader2, RefreshCw, Search } from "lucide-react";
import { useState } from "react";
import api from "../api/api";

function SearchAspect({ uploadId }) {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("info");
  const [isLoading, setIsLoading] = useState(false);

  const runSearch = async (aspectName) => {
    const cleanAspectName = aspectName.trim();

    if (!cleanAspectName) {
      setResult(null);
      setMessageType("info");
      setMessage("Type an aspect name to search.");
      return;
    }

    try {
      setIsLoading(true);
      setMessage("");
      setResult(null);

      const response = await api.get(
        uploadId
          ? `/analytics/aspect/${uploadId}/${encodeURIComponent(cleanAspectName)}`
          : `/analytics/aspect/${encodeURIComponent(cleanAspectName)}`
      );

      if (response.data.message) {
        setMessageType("info");
        setMessage(`No results found for "${cleanAspectName}". Try another aspect.`);
        return;
      }

      setResult(response.data);
    } catch (err) {
      console.log(err);
      setMessageType("error");
      setMessage("Unable to search this aspect right now. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const searchAspect = (event) => {
    event.preventDefault();
    runSearch(query);
  };

  return (
    <section className="rounded-xl bg-white p-8 shadow">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-sky-700">
            Aspect Lookup
          </p>

          <h2 className="mt-2 text-2xl font-bold text-slate-950">
            Search Aspect
          </h2>
        </div>
      </div>

      <form
        onSubmit={searchAspect}
        className="mt-6 flex flex-col gap-3 sm:flex-row"
      >
        <div className="relative flex-1">
          <Search
            className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
            size={20}
          />

          <input
            type="text"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search for an aspect, e.g. price, delivery, support"
            className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-12 pr-4 text-slate-900 outline-none transition focus:border-sky-400 focus:bg-white focus:ring-4 focus:ring-sky-100"
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {isLoading ? <Loader2 className="animate-spin" size={18} /> : <Search size={18} />}
          {isLoading ? "Searching..." : "Search"}
        </button>
      </form>

      {message && (
        <div
          className={`mt-5 flex items-start justify-between gap-3 rounded-xl border px-4 py-3 animate-fade-in ${
            messageType === "error"
              ? "border-rose-200 bg-rose-50 text-rose-800"
              : "border-amber-200 bg-amber-50 text-amber-800"
          }`}
        >
          <div className="flex items-start gap-3">
          <AlertCircle className="mt-0.5 shrink-0" size={20} />
          <p className="text-sm font-semibold">{message}</p>
          </div>

          {messageType === "error" && (
            <button
              type="button"
              onClick={() => runSearch(query)}
              className="inline-flex shrink-0 items-center gap-2 rounded-lg bg-rose-600 px-3 py-2 text-xs font-semibold text-white hover:bg-rose-700"
            >
              <RefreshCw size={14} />
              Retry
            </button>
          )}
        </div>
      )}

      {result && (
        <div className="mt-6 animate-fade-in">
          <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-500">
                Search result
              </p>

              <h3 className="text-2xl font-bold capitalize text-slate-950">
                {result.aspect}
              </h3>
            </div>

            <p className="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-600">
              {result.mentions} mentions
            </p>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard label="Mention count" value={result.mentions} />
            <MetricCard
              label="Positive"
              value={`${result.positive_percentage}%`}
              tone="emerald"
            />
            <MetricCard
              label="Negative"
              value={`${result.negative_percentage}%`}
              tone="rose"
            />
            <MetricCard
              label="Neutral"
              value={`${result.neutral_percentage}%`}
              tone="amber"
            />
          </div>
        </div>
      )}
    </section>
  );
}

function MetricCard({ label, value, tone = "slate" }) {
  const tones = {
    slate: "bg-slate-50 text-slate-900",
    emerald: "bg-emerald-50 text-emerald-700",
    rose: "bg-rose-50 text-rose-700",
    amber: "bg-amber-50 text-amber-700",
  };

  return (
    <div className={`rounded-2xl border border-slate-200 p-5 ${tones[tone]}`}>
      <p className="text-sm font-semibold uppercase tracking-wide opacity-75">
        {label}
      </p>

      <p className="mt-2 text-3xl font-bold">{value}</p>
    </div>
  );
}

export default SearchAspect;
