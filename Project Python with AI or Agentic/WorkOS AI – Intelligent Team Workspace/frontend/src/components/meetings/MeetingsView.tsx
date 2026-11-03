import React, { useState } from 'react';
import {
  Video,
  FileText,
  CheckCircle2,
  Plus,
  Sparkles,
  ArrowRight,
  Clock,
  User,
} from 'lucide-react';
import { Meeting } from '../../types';

export const MeetingsView: React.FC = () => {
  const [transcript, setTranscript] = useState(
    "Sarah: Let's finalize the Stripe webhook integration by Friday. Alex, can you review the schema migration for task dependencies? Alex: Yes, I will deploy the pgvector index updates before tomorrow's standup."
  );

  const [meetings, setMeetings] = useState<Meeting[]>([
    {
      id: 'm-1',
      workspace_id: 'ws-1',
      title: 'Sprint 3 Planning & Architecture Sync',
      summary: 'Team aligned on 8-week delivery milestones and Stripe webhook isolation.',
      key_decisions: [
        'Enforce strict workspace_id filtering across all pgvector embedding tables.',
        'Stripe webhook sandbox integration set as immediate priority.',
      ],
      created_at: '2026-11-02T10:00:00Z',
      action_items: [
        {
          id: 'ai-1',
          meeting_id: 'm-1',
          action_text: 'Review and execute pgvector index schema migration',
          suggested_due_date: '2026-11-04',
          status: 'converted',
        },
        {
          id: 'ai-2',
          meeting_id: 'm-1',
          action_text: 'Configure SSL certificate for Stripe webhook testing',
          suggested_due_date: '2026-11-06',
          status: 'pending',
        },
      ],
    },
  ]);

  const handleConvertAction = (meetingId: string, actionId: string) => {
    setMeetings((prev) =>
      prev.map((m) => {
        if (m.id !== meetingId) return m;
        return {
          ...m,
          action_items: m.action_items?.map((item) =>
            item.id === actionId ? { ...item, status: 'converted' } : item
          ),
        };
      })
    );
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* View Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">Meeting Intelligence & Action Extraction</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Upload meeting notes or audio transcripts to automatically extract decisions, pending work, and assignable tasks.
          </p>
        </div>
      </div>

      {/* Transcript Input Box */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
        <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
          Paste Raw Meeting Notes or Transcript
        </label>
        <textarea
          rows={3}
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          className="w-full p-3 text-sm rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-xs"
        />

        <div className="flex justify-end">
          <button className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm transition">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Process Transcript with AI</span>
          </button>
        </div>
      </div>

      {/* Extracted Meeting Insights */}
      <div className="space-y-4">
        {meetings.map((meeting) => (
          <div
            key={meeting.id}
            className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-5"
          >
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-950 flex items-center justify-center text-purple-600">
                  <Video className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold">{meeting.title}</h3>
                  <span className="text-[11px] text-slate-500">Logged on {new Date(meeting.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>

            {/* Key Decisions */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Key Decisions Agreed
              </h4>
              <ul className="space-y-1.5">
                {meeting.key_decisions.map((dec, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-slate-700 dark:text-slate-300">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{dec}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Action Items */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Extracted Action Items
              </h4>
              <div className="space-y-2">
                {meeting.action_items?.map((item) => (
                  <div
                    key={item.id}
                    className="p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 flex items-center justify-between gap-4"
                  >
                    <div>
                      <p className="text-xs font-semibold text-slate-900 dark:text-slate-100">{item.action_text}</p>
                      <div className="flex items-center gap-3 text-[11px] text-slate-500 mt-1">
                        <span>Due: {item.suggested_due_date}</span>
                        <span>•</span>
                        <span>Assigned to: Team Lead</span>
                      </div>
                    </div>

                    <div>
                      {item.status === 'converted' ? (
                        <span className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 px-2.5 py-1 rounded-md bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800">
                          Active in Kanban
                        </span>
                      ) : (
                        <button
                          onClick={() => handleConvertAction(meeting.id, item.id)}
                          className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md text-xs font-semibold transition"
                        >
                          <Plus className="w-3 h-3" />
                          <span>Convert to Task</span>
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

