import React from 'react';
import {
  BarChart3,
  AlertTriangle,
  CheckCircle2,
  TrendingDown,
  ArrowRight,
  ShieldAlert,
  GitBranch,
} from 'lucide-react';

export const AnalyticsView: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold">AI Project Risk Detection Engine</h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Predictive delivery analysis evaluating task completion rates, blocked dependencies, and critical path bottlenecks.
        </p>
      </div>

      {/* Health Score Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Sprint Health Score
          </span>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-4xl font-extrabold text-indigo-600 dark:text-indigo-400">92</span>
            <span className="text-sm font-semibold text-slate-500">/ 100</span>
          </div>
          <span className="inline-block mt-2 text-xs font-semibold px-2 py-0.5 rounded bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
            Low Delivery Risk
          </span>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Blocked Dependency Paths
          </span>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-4xl font-extrabold text-rose-600 dark:text-rose-400">1</span>
            <span className="text-sm font-semibold text-slate-500">task blocked</span>
          </div>
          <p className="mt-2 text-[11px] text-slate-500">
            Stripe Webhook Gateway is delaying 2 downstream checkout tasks.
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Confirmed Slippage
          </span>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-4xl font-extrabold text-amber-600 dark:text-amber-400">0</span>
            <span className="text-sm font-semibold text-slate-500">overdue tasks</span>
          </div>
          <p className="mt-2 text-[11px] text-slate-500">
            All active sprint deliverables are currently within estimated timeline margins.
          </p>
        </div>
      </div>

      {/* Critical Path Bottlenecks */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex items-center gap-2 text-rose-600 dark:text-rose-400">
          <ShieldAlert className="w-4 h-4" />
          <h3 className="text-sm font-bold uppercase tracking-wider">Identified Critical Path Bottlenecks</h3>
        </div>

        <div className="p-4 rounded-lg border border-rose-200 dark:border-rose-900/60 bg-rose-50/50 dark:bg-rose-950/20 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-rose-900 dark:text-rose-200">
              Task: Stripe Webhook Gateway & Payment Flow
            </span>
            <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-rose-200 text-rose-800 dark:bg-rose-900 dark:text-rose-200">
              Blocked Status
            </span>
          </div>
          <p className="text-xs text-rose-800 dark:text-rose-300 leading-relaxed">
            Root Cause: Awaiting SSL certificate registration. Downstream impact: Directly halts "Checkout UI Integration" and "Order Email Notification" milestones.
          </p>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
          AI Actionable Recommendations
        </h3>

        <div className="space-y-3">
          {[
            {
              title: 'Reassign 1 Backend Engineer to Stripe SSL Endpoint',
              description: 'Resolving this bottleneck within the next 48 hours eliminates risk of slipping Phase 2 delivery.',
            },
            {
              title: 'Pre-seed pgvector Test Embeddings in Staging',
              description: 'Prevents database indexing latency when the team performs initial acceptance testing.',
            },
          ].map((rec, i) => (
            <div
              key={i}
              className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 flex items-center justify-between"
            >
              <div>
                <p className="text-xs font-semibold">{rec.title}</p>
                <p className="text-[11px] text-slate-500 mt-0.5">{rec.description}</p>
              </div>
              <button className="px-3 py-1 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-50 rounded-md text-xs font-semibold transition shrink-0 ml-4">
                Review Action
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

