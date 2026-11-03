import React, { useState } from 'react';
import { useAuthStore } from './store/useAuthStore';
import { AuthPage } from './components/auth/AuthPage';
import { DashboardLayout } from './layouts/DashboardLayout';
import { OverviewView } from './components/dashboard/OverviewView';
import { KanbanBoard } from './components/tasks/KanbanBoard';
import { AIAssistantDrawer } from './components/ai-assistant/AIAssistantDrawer';
import { MeetingsView } from './components/meetings/MeetingsView';
import { AnalyticsView } from './components/analytics/AnalyticsView';

export const App: React.FC = () => {
  const { isAuthenticated, user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<string>('dashboard');

  // FIRST PAGE: If user is not authenticated, render Login / Sign In / Sign Up page!
  if (!isAuthenticated) {
    return <AuthPage />;
  }

  const renderActiveView = () => {
    switch (activeTab) {
      case 'dashboard':
        return <OverviewView onNavigate={setActiveTab} />;
      case 'board':
        return <KanbanBoard />;
      case 'ai-assistant':
        return <AIAssistantDrawer />;
      case 'meetings':
        return <MeetingsView />;
      case 'analytics':
        return <AnalyticsView />;
      case 'projects':
        return (
          <div className="max-w-5xl mx-auto space-y-4">
            <h1 className="text-xl font-bold">Workspace Projects</h1>
            <p className="text-xs text-slate-500">Manage and track multi-phase initiatives across the organization.</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
                <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">Active</span>
                <h3 className="text-sm font-bold mt-2">E-Commerce Application Platform</h3>
                <p className="text-xs text-slate-500 mt-1">Full-stack e-commerce implementation with Stripe payments and live Kanban.</p>
                <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
                  <span>8 Milestones</span>
                  <button onClick={() => setActiveTab('board')} className="text-indigo-600 font-semibold hover:underline">Open Board →</button>
                </div>
              </div>
            </div>
          </div>
        );
      case 'team':
        return (
          <div className="max-w-4xl mx-auto space-y-4">
            <h1 className="text-xl font-bold">Team Members & Access Control</h1>
            <p className="text-xs text-slate-500">Tenant-isolated workspace roles (Owner, Admin, Member, Viewer).</p>
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
                  <tr>
                    <th className="p-3 font-semibold text-slate-600 dark:text-slate-300">Name</th>
                    <th className="p-3 font-semibold text-slate-600 dark:text-slate-300">Email</th>
                    <th className="p-3 font-semibold text-slate-600 dark:text-slate-300">Role</th>
                    <th className="p-3 font-semibold text-slate-600 dark:text-slate-300">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  <tr>
                    <td className="p-3 font-medium">{user?.full_name || 'Current User'}</td>
                    <td className="p-3 text-slate-500">{user?.email || 'user@workos.ai'}</td>
                    <td className="p-3"><span className="px-2 py-0.5 rounded bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300 font-bold text-[10px]">OWNER</span></td>
                    <td className="p-3 text-emerald-600 font-medium">Active</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-medium">Alex Rivera</td>
                    <td className="p-3 text-slate-500">alex@workos.ai</td>
                    <td className="p-3"><span className="px-2 py-0.5 rounded bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300 font-bold text-[10px]">ADMIN</span></td>
                    <td className="p-3 text-emerald-600 font-medium">Active</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        );
      case 'settings':
        return (
          <div className="max-w-3xl mx-auto space-y-4">
            <h1 className="text-xl font-bold">Workspace Settings</h1>
            <p className="text-xs text-slate-500">Configure workspace name, vector search indices, and API integrations.</p>
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400">Workspace Name</label>
                <input type="text" defaultValue={`${user?.full_name || 'My'}'s Workspace`} className="mt-1 w-full p-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-md" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400">Active User</label>
                <input type="text" readOnly defaultValue={`${user?.full_name} (${user?.email})`} className="mt-1 w-full p-2 text-xs font-mono bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-md text-slate-500" />
              </div>
            </div>
          </div>
        );
      default:
        return <OverviewView onNavigate={setActiveTab} />;
    }
  };

  return (
    <DashboardLayout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderActiveView()}
    </DashboardLayout>
  );
};

export default App;
