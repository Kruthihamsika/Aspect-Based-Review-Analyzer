import { AlertTriangle, Inbox, Loader2, RefreshCw } from "lucide-react";

export function Spinner({ label = "Loading" }) {
  return (
    <div className="flex items-center gap-2 text-sm font-semibold text-slate-500">
      <Loader2 className="animate-spin text-sky-600" size={18} />
      <span>{label}</span>
    </div>
  );
}

export function SkeletonBlock({ className = "" }) {
  return (
    <div
      className={`animate-pulse rounded-xl bg-slate-200/80 ${className}`}
      aria-hidden="true"
    />
  );
}

export function EmptyState({
  title = "No data yet",
  message = "Upload a review dataset to populate this section.",
}) {
  return (
    <div className="flex min-h-56 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white text-slate-400 shadow-sm">
        <Inbox size={24} />
      </div>

      <h3 className="mt-4 text-base font-bold text-slate-900">{title}</h3>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
        {message}
      </p>
    </div>
  );
}

export function ErrorState({
  title = "Something went wrong",
  message = "We could not load this data.",
  onRetry,
}) {
  return (
    <div className="flex min-h-56 flex-col items-center justify-center rounded-2xl border border-rose-200 bg-rose-50 px-6 py-10 text-center text-rose-800">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white text-rose-600 shadow-sm">
        <AlertTriangle size={24} />
      </div>

      <h3 className="mt-4 text-base font-bold">{title}</h3>
      <p className="mt-2 max-w-md text-sm leading-6">{message}</p>

      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-5 inline-flex items-center gap-2 rounded-lg bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700"
        >
          <RefreshCw size={16} />
          Retry
        </button>
      )}
    </div>
  );
}
