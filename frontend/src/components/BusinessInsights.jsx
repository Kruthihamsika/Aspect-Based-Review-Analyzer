import {
  BarChart3,
  CheckCircle2,
  Lightbulb,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import api from "../api/api";
import { EmptyState, ErrorState, SkeletonBlock } from "./DashboardStates";

function BusinessInsights({ uploadId }) {
  const [dashboard, setDashboard] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadInsights = async () => {
    try {
      setIsLoading(true);
      setError("");

      const response = await api.get(
        uploadId ? `/analytics/dashboard/${uploadId}` : "/analytics/dashboard"
      );
      setDashboard(response.data);
    } catch (err) {
      console.log(err);
      setError("Unable to load business insights.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadInsights();
  }, [uploadId]);

  const insights = useMemo(() => {
    if (!dashboard) {
      return null;
    }

    const summary = dashboard.summary || {};
    const positiveAspects = dashboard.top_positive_aspects || [];
    const negativeAspects = dashboard.top_negative_aspects || [];
    const sentiments = dashboard.sentiment_distribution || {};

    const totalSentiments =
      (sentiments.Positive || 0) +
      (sentiments.Negative || 0) +
      (sentiments.Neutral || 0);

    const satisfaction =
      totalSentiments > 0
        ? Math.round(((sentiments.Positive || 0) / totalSentiments) * 100)
        : 0;

    const praisedAspect = positiveAspects[0];
    const criticizedAspect = negativeAspects[0];

    const recommendations = createRecommendations(
      praisedAspect,
      criticizedAspect,
      satisfaction
    );

    return {
      summary,
      satisfaction,
      praisedAspect,
      criticizedAspect,
      recommendations,
      hasData:
        (summary.total_reviews || 0) > 0 ||
        positiveAspects.length > 0 ||
        negativeAspects.length > 0 ||
        totalSentiments > 0,
    };
  }, [dashboard]);

  if (isLoading) {
    return (
      <section className="rounded-xl bg-white p-8 shadow">
        <div className="flex items-center justify-between gap-4">
          <div>
            <SkeletonBlock className="h-4 w-40" />
            <SkeletonBlock className="mt-3 h-8 w-56" />
          </div>
          <SkeletonBlock className="h-10 w-36 rounded-full" />
        </div>

        <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-4">
          {[1, 2, 3, 4].map((item) => (
            <SkeletonBlock key={item} className="h-40" />
          ))}
        </div>

        <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-5">
          <SkeletonBlock className="h-48 lg:col-span-3" />
          <SkeletonBlock className="h-48 lg:col-span-2" />
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="rounded-xl bg-white p-8 shadow">
        <ErrorState message={error} onRetry={loadInsights} />
      </section>
    );
  }

  if (!insights) {
    return null;
  }

  if (!insights.hasData) {
    return (
      <section className="rounded-xl bg-white p-8 shadow">
        <EmptyState
          title="No insights yet"
          message="Upload review data to generate executive summaries and recommendations."
        />
      </section>
    );
  }

  return (
    <section className="rounded-xl bg-white p-8 shadow animate-fade-in">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-sky-700">
            Business Intelligence
          </p>

          <h2 className="mt-2 text-2xl font-bold text-slate-950">
            Business Insights
          </h2>
        </div>

        <div className="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-600">
          {insights.summary.total_reviews || 0} reviews analyzed
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-4">
        <InsightCard
          icon={<ThumbsUp size={22} />}
          label="Most praised aspect"
          value={insights.praisedAspect?.aspect || "No positive aspect yet"}
          detail={formatAspectDetail(insights.praisedAspect, "positive")}
          tone="emerald"
        />

        <InsightCard
          icon={<ThumbsDown size={22} />}
          label="Most criticized aspect"
          value={insights.criticizedAspect?.aspect || "No negative aspect yet"}
          detail={formatAspectDetail(insights.criticizedAspect, "negative")}
          tone="rose"
        />

        <InsightCard
          icon={<BarChart3 size={22} />}
          label="Customer satisfaction"
          value={`${insights.satisfaction}%`}
          detail={getSatisfactionLabel(insights.satisfaction)}
          tone="sky"
        />

        <InsightCard
          icon={<CheckCircle2 size={22} />}
          label="Total aspects"
          value={insights.summary.total_aspects || 0}
          detail="Aspect mentions detected"
          tone="indigo"
        />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-5">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 lg:col-span-3">
          <div className="flex items-center gap-2 text-slate-900">
            <Sparkles className="text-sky-600" size={22} />
            <h3 className="font-bold">Executive Summary</h3>
          </div>

          <p className="mt-3 leading-7 text-slate-600">
            {createExecutiveSummary(insights)}
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 lg:col-span-2">
          <div className="flex items-center gap-2 text-slate-900">
            <Lightbulb className="text-amber-500" size={22} />
            <h3 className="font-bold">Improvement Recommendations</h3>
          </div>

          <ul className="mt-4 space-y-3">
            {insights.recommendations.map((recommendation) => (
              <li
                key={recommendation}
                className="rounded-xl border border-white bg-white px-4 py-3 text-sm leading-6 text-slate-600 shadow-sm"
              >
                {recommendation}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

function InsightCard({ icon, label, value, detail, tone }) {
  const tones = {
    emerald: "border-emerald-100 bg-emerald-50 text-emerald-700",
    rose: "border-rose-100 bg-rose-50 text-rose-700",
    sky: "border-sky-100 bg-sky-50 text-sky-700",
    indigo: "border-indigo-100 bg-indigo-50 text-indigo-700",
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
      <div
        className={`mb-4 flex h-11 w-11 items-center justify-center rounded-xl border ${tones[tone]}`}
      >
        {icon}
      </div>

      <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <h3 className="mt-2 truncate text-2xl font-bold text-slate-950">
        {value}
      </h3>

      <p className="mt-2 text-sm leading-6 text-slate-600">{detail}</p>
    </div>
  );
}

function formatAspectDetail(aspect, sentiment) {
  if (!aspect) {
    return "Upload reviews to generate this insight.";
  }

  const percentage = aspect[`${sentiment}_percentage`];
  const count = aspect[`${sentiment}_count`];

  if (percentage !== undefined) {
    return `${percentage}% ${sentiment} sentiment across ${aspect.total_count || 0} mentions`;
  }

  return `${count || 0} ${sentiment} mentions detected`;
}

function getSatisfactionLabel(satisfaction) {
  if (satisfaction >= 75) {
    return "Strong customer sentiment";
  }

  if (satisfaction >= 50) {
    return "Healthy but improvable";
  }

  if (satisfaction > 0) {
    return "Needs focused improvement";
  }

  return "No sentiment data yet";
}

function createRecommendations(praisedAspect, criticizedAspect, satisfaction) {
  const recommendations = [];

  if (criticizedAspect) {
    recommendations.push(
      `Prioritize ${criticizedAspect.aspect}; it has ${
        criticizedAspect.negative_percentage || 0
      }% negative sentiment.`
    );
  }

  if (praisedAspect) {
    recommendations.push(
      `Promote ${praisedAspect.aspect}; customers mention it positively.`
    );
  }

  if (satisfaction < 50) {
    recommendations.push(
      "Review recurring complaints and create a short-term service recovery plan."
    );
  } else {
    recommendations.push(
      "Keep monitoring sentiment trends after each new review upload."
    );
  }

  return recommendations;
}

function createExecutiveSummary(insights) {
  const praised = insights.praisedAspect?.aspect;
  const criticized = insights.criticizedAspect?.aspect;

  if (!praised && !criticized) {
    return "Upload and analyze review data to generate a business summary.";
  }

  const satisfactionText = `${insights.satisfaction}% overall customer satisfaction`;

  if (praised && criticized) {
    return `Customers are most positive about ${praised}, while ${criticized} is the clearest improvement opportunity. The dashboard currently shows ${satisfactionText}, based on detected aspect sentiment across the uploaded reviews.`;
  }

  if (praised) {
    return `Customers are responding well to ${praised}. The dashboard currently shows ${satisfactionText}, with limited negative patterns detected so far.`;
  }

  return `${criticized} is the main area requiring attention. The dashboard currently shows ${satisfactionText}, so improving this aspect should have a visible impact.`;
}

export default BusinessInsights;
