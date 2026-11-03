import React, { useState } from 'react';
import {
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  Send,
  Loader2,
  GitFork,
  Calendar,
  Users,
} from 'lucide-react';
import { GeneratedPlan } from '../../types';

export const AIAssistantDrawer: React.FC = () => {
  const [brief, setBrief] = useState('Build an e-commerce application within 8 weeks including Stripe payments, product catalog, cart, and authentication.');
  const [isGenerating, setIsGenerating] = useState(false);
  const [stagedPlan, setStagedPlan] = useState<GeneratedPlan | null>({
    project_name: 'E-Commerce Platform Launch',
    summary: '8-week full-stack e-commerce implementation with multi-tenant isolation, Stripe payments, and live Kanban.',
    suggested_timeline_weeks: 8,
    milestones: [
      {
        title: 'Phase 1: Architecture, Core Schemas & Auth',
        week_number: 1,
        tasks: [
          {
            temp_id: 't1',
            title: 'Design Relational Schema & Tenant Isolation',
            description: 'PostgreSQL models, foreign keys, and workspace member role guards.',
            priority: 'urgent',
            estimated_hours: 20,
            role_suggestion: 'Backend Architect',
            depends_on: [],
          },
          {
            temp_id: 't2',
            title: 'Setup JWT Authentication & User Sessions',
            description: 'Signup, login, password hashing, and token refresh endpoints.',
            priority: 'high',
            estimated_hours: 16,
            role_suggestion: 'Backend Engineer',
            depends_on: ['t1'],
          },
        ],
      },
      {
        title: 'Phase 2: Core Domain Features & Business Logic',
        week_number: 3,
        tasks: [
          {
            temp_id: 't3',
            title: 'Build Product Catalog & Inventory Service',
            description: 'CRUD APIs for items, stock reservation, and search filtering.',
            priority: 'high',
            estimated_hours: 32,
            role_suggestion: 'Full Stack Engineer',
            depends_on: ['t1'],
          },
          {
            temp_id: 't4',
            title: 'Stripe Webhook Gateway & Payment Flow',
            description: 'Payment intent creation, checkout sessions, and webhook idempotency.',
            priority: 'urgent',
            estimated_hours: 40,
            role_suggestion: 'Senior Backend Engineer',
            depends_on: ['t2', 't3'],
          },
        ],
      },
      {
        title: 'Phase 3: Real-Time Collaboration & Delivery',
        week_number: 6,
        tasks: [
          {
            temp_id: 't5',
            title: 'FastAPI WebSockets & Redis Pub/Sub Broadcast',
            description: 'Synchronized live kanban card dragging and user presence.',
            priority: 'medium',
            estimated_hours: 24,
            role_suggestion: 'Frontend Engineer',
            depends_on: ['t3'],
          },
        ],
      },
    ],
    identified_risks: [
      'Stripe Webhook gateway dependencies can delay end-to-end checkout validation if sandbox keys are delayed.',
      'WebSocket reconnection handling across mobile clients requires exponential backoff.',
    ],
    suggested_team_roles: [
      'Technical Lead / Architect',
      'Senior Backend Engineer (Python / FastAPI)',
      'Frontend Engineer (React / TypeScript)',
      'QA / Release Specialist',
    ],
  });

  const [approvalStatus, setApprovalStatus] = useState<'pending' | 'approved' | 'rejected'>('pending');

  const handleGenerate = () => {
    setIsGenerating(true);
    setApprovalStatus('pending');
    setTimeout(() => {
      setIsGenerating(false);
    }, 800);
  };

  const handleApprove = () => {
    setApprovalStatus('approved');
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold">AI Project Planning Agent</h1>
            <span className="px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 text-xs font-semibold">
              ReAct Framework
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Provide a natural-language brief; the agent will extract requirements, divide into milestones, and calculate task dependencies.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-800 text-xs bg-white dark:bg-slate-900 shadow-2xs">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span className="font-medium">Human-in-the-Loop Guard Enabled</span>
        </div>
      </div>

      {/* Input Brief Section */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
        <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
          Project Brief or Business Requirements
        </label>
        <textarea
          rows={3}
          value={brief}
          onChange={(e) => setBrief(e.target.value)}
          placeholder="e.g., Build an e-commerce application within 8 weeks..."
          className="w-full p-3 text-sm rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 text-xs text-slate-500">
            <span>Target: <strong>8 Weeks</strong></span>
            <span>•</span>
            <span>Target Velocity: <strong>~30h/week</strong></span>
          </div>
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-50"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Generating Plan...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>Generate Plan</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Staged Plan Review Area */}
      {stagedPlan && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-6">
          {/* Staged Banner & Approval Box */}
          <div className="flex items-center justify-between p-4 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
                  Staged AI Action Proposal
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-700">
                  Status: {approvalStatus.toUpperCase()}
                </span>
              </div>
              <h3 className="text-base font-bold mt-1">{stagedPlan.project_name}</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{stagedPlan.summary}</p>
            </div>

            <div className="flex items-center gap-3">
              {approvalStatus === 'pending' ? (
                <>
                  <button
                    onClick={() => setApprovalStatus('rejected')}
                    className="px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-md transition"
                  >
                    Reject
                  </button>
                  <button
                    onClick={handleApprove}
                    className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-md shadow-sm transition"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Approve & Publish to Kanban</span>
                  </button>
                </>
              ) : approvalStatus === 'approved' ? (
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 text-xs font-bold border border-emerald-300 dark:border-emerald-800">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Approved & Committed to Database</span>
                </div>
              ) : (
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300 text-xs font-bold border border-rose-300 dark:border-rose-800">
                  <span>Rejected by Admin</span>
                </div>
              )}
            </div>
          </div>

          {/* Milestones and Generated Tasks */}
          <div className="space-y-4">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Project Milestones & Task Breakdown
            </h4>

            {stagedPlan.milestones.map((milestone, idx) => (
              <div key={idx} className="border border-slate-200 dark:border-slate-800 rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-indigo-600" />
                    <span className="text-xs font-bold">{milestone.title}</span>
                  </div>
                  <span className="text-[11px] text-slate-500 font-mono">Week {milestone.week_number}</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                  {milestone.tasks.map((task) => (
                    <div
                      key={task.temp_id}
                      className="p-3 rounded-md bg-slate-50 dark:bg-slate-800/40 border border-slate-200/70 dark:border-slate-800 space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold">{task.title}</span>
                        <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                          {task.priority}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 leading-relaxed">{task.description}</p>
                      <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-200/50 dark:border-slate-800">
                        <span>Role: {task.role_suggestion}</span>
                        <span>Est: {task.estimated_hours}h</span>
                      </div>
                      {task.depends_on.length > 0 && (
                        <div className="flex items-center gap-1 text-[10px] text-indigo-600 dark:text-indigo-400 font-mono">
                          <GitFork className="w-3 h-3" />
                          <span>Depends on: {task.depends_on.join(', ')}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Identified Risks & Suggested Roles */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div className="p-4 rounded-lg bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800/50">
              <div className="flex items-center gap-2 text-amber-800 dark:text-amber-300 font-semibold text-xs mb-2">
                <AlertTriangle className="w-4 h-4" />
                <span>Detected Delivery Risks</span>
              </div>
              <ul className="list-disc list-inside text-xs text-amber-900 dark:text-amber-200 space-y-1">
                {stagedPlan.identified_risks.map((risk, i) => (
                  <li key={i} className="leading-relaxed">{risk}</li>
                ))}
              </ul>
            </div>

            <div className="p-4 rounded-lg bg-indigo-50/60 dark:bg-indigo-950/20 border border-indigo-200 dark:border-indigo-800/50">
              <div className="flex items-center gap-2 text-indigo-800 dark:text-indigo-300 font-semibold text-xs mb-2">
                <Users className="w-4 h-4" />
                <span>Recommended Team Roles</span>
              </div>
              <ul className="list-disc list-inside text-xs text-indigo-900 dark:text-indigo-200 space-y-1">
                {stagedPlan.suggested_team_roles.map((role, i) => (
                  <li key={i} className="leading-relaxed">{role}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

