import React from 'react';
import {
  FolderGit2,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';

interface OverviewViewProps {
  onNavigate: (tab: string) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({ onNavigate }) => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-800 p-8 text-white shadow-lg">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-xs font-semibold mb-4 text-indigo-100">
            <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
            AI Operating System for Teams
          </div>
          <h1 className="text-3xl font-bold tracking-tight">
            WorkOS AI Team Workspace
          </h1>
          <p className="mt-2 text-indigo-100 text-sm leading-relaxed">
            Autonomous project graph generation, delivery risk detection, and RAG knowledge search with strict tenant isolation and human-in-the-loop approvals.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('ai-assistant')}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white text-indigo-700 font-semibold text-sm rounded-lg hover:bg-indigo-50 transition shadow-sm"
            >
              <Sparkles className="w-4 h-4 text-indigo-600" />
              Generate Project Plan
            </button>
            <button
              onClick={() => onNavigate('board')}
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-800/80 hover:bg-indigo-800 text-white font-medium text-sm rounded-lg transition"
            >
              Open Kanban Board
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* KPI Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Active Projects</span>
            <FolderGit2 className="w-5 h-5 text-indigo-600" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold">4</span>
            <span className="text-xs text-emerald-600 font-medium">100% On Track</span>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Completed Tasks</span>
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold">28</span>
            <span className="text-xs text-slate-500">/ 36 total</span>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Delivery Health Score</span>
            <TrendingUp className="w-5 h-5 text-indigo-500" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">92 / 100</span>
            <span className="text-xs text-emerald-600 font-medium">Low Risk</span>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Pending AI Actions</span>
            <AlertTriangle className="w-5 h-5 text-amber-500" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-amber-600 dark:text-amber-400">1</span>
            <span className="text-xs text-amber-600 font-medium">Requires Approval</span>
          </div>
        </div>
      </div>

      {/* Two Column Section: Recent Projects & AI Intelligence Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Projects */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold">Active Workspace Projects</h2>
            <button
              onClick={() => onNavigate('projects')}
              className="text-xs text-indigo-600 dark:text-indigo-400 font-medium hover:underline"
            >
              View all
            </button>
          </div>
          <div className="space-y-3">
            {[
              {
                name: 'E-Commerce Platform Launch',
                status: 'active',
                progress: 75,
                dueDate: 'Dec 28, 2026',
                lead: 'Sarah Connor',
              },
              {
                name: 'Core Agentic RAG Pipeline',
                status: 'active',
                progress: 90,
                dueDate: 'Nov 20, 2026',
                lead: 'Alex Rivera',
              },
              {
                name: 'Mobile App React Native Bridge',
                status: 'planning',
                progress: 30,
                dueDate: 'Jan 15, 2027',
                lead: 'David Kim',
              },
            ].map((p, idx) => (
              <div
                key={idx}
                className="p-4 rounded-lg border border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-800/30 flex items-center justify-between"
              >
                <div>
                  <h3 className="text-sm font-semibold">{p.name}</h3>
                  <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                    <span>Due: {p.dueDate}</span>
                    <span>•</span>
                    <span>Lead: {p.lead}</span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">{p.progress}%</span>
                  <div className="w-24 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full mt-1 overflow-hidden">
                    <div className="h-full bg-indigo-600 rounded-full" style={{ width: `${p.progress}%` }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: AI Action Governance Guard */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 font-semibold text-sm">
              <ShieldCheck className="w-4 h-4" />
              <span>AI Governance & Safety</span>
            </div>
            <h3 className="text-base font-semibold mt-2">Human-in-the-Loop Gating</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
              All AI write operations (generating projects, mutating deadlines, or bulk creating tasks) require explicit confirmation from a workspace administrator before execution.
            </p>

            <div className="mt-4 p-3 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-semibold text-amber-900 dark:text-amber-200">
                    Staged Plan Awaiting Review
                  </p>
                  <p className="text-[11px] text-amber-700 dark:text-amber-300 mt-0.5">
                    "E-Commerce Platform" (5 milestones, 8 tasks)
                  </p>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={() => onNavigate('ai-assistant')}
            className="w-full mt-6 py-2 px-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold transition"
          >
            Review Staged Plan
          </button>
        </div>
      </div>
    </div>
  );
};

