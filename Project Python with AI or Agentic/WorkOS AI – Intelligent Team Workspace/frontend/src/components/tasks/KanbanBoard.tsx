import React, { useState, useEffect } from 'react';
import {
  Plus,
  Clock,
  AlertCircle,
  CheckCircle2,
  GitBranch,
  MoreVertical,
  User as UserIcon,
  X,
  Trash2,
  Edit2,
  ArrowRight,
  ArrowLeft,
  Search,
  MessageSquare,
  Send,
  Filter,
} from 'lucide-react';
import { Task, TaskStatus, TaskPriority } from '../../types';
import { useAuthStore } from '../../store/useAuthStore';

interface KanbanBoardProps {
  onTaskClick?: (task: Task) => void;
}

const DEFAULT_TASKS: Task[] = [
  {
    id: 't-1',
    workspace_id: 'ws-1',
    project_id: 'p-1',
    title: 'Design PostgreSQL Models with Tenant Isolation',
    description: 'Enforce non-nullable workspace_id foreign key constraints and composite indexes.',
    status: 'completed',
    priority: 'urgent',
    estimated_hours: 16,
    actual_hours: 14,
    created_at: '2026-11-01',
    dependency_ids: [],
  },
  {
    id: 't-2',
    workspace_id: 'ws-1',
    project_id: 'p-1',
    title: 'Implement JWT Authentication & RBAC Guard',
    description: 'FastAPI dependency for owner/admin/member/viewer role enforcement.',
    status: 'in_progress',
    priority: 'high',
    estimated_hours: 20,
    actual_hours: 8,
    created_at: '2026-11-01',
    dependency_ids: ['t-1'],
  },
  {
    id: 't-3',
    workspace_id: 'ws-1',
    project_id: 'p-1',
    title: 'Stripe Webhook Gateway & Payment Flow',
    description: 'Awaiting SSL test domain configuration before sandbox webhook verification.',
    status: 'blocked',
    priority: 'urgent',
    estimated_hours: 32,
    actual_hours: 12,
    created_at: '2026-11-02',
    dependency_ids: ['t-2'],
  },
  {
    id: 't-4',
    workspace_id: 'ws-1',
    project_id: 'p-1',
    title: 'Real-Time WebSocket Sync via Redis Pub/Sub',
    description: 'Multi-node event propagation for live Kanban and presence updates.',
    status: 'todo',
    priority: 'medium',
    estimated_hours: 18,
    actual_hours: 0,
    created_at: '2026-11-02',
    dependency_ids: ['t-2'],
  },
  {
    id: 't-5',
    workspace_id: 'ws-1',
    project_id: 'p-1',
    title: 'AI ReAct Agent Planning & Approval Gating',
    description: 'Staging engine ensuring writes require human admin approval.',
    status: 'review',
    priority: 'high',
    estimated_hours: 24,
    actual_hours: 22,
    created_at: '2026-11-02',
    dependency_ids: ['t-1'],
  },
];

const COLUMNS: { id: TaskStatus; label: string; color: string; badgeBg: string }[] = [
  { id: 'todo', label: 'To Do', color: 'bg-slate-400', badgeBg: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300' },
  { id: 'in_progress', label: 'In Progress', color: 'bg-indigo-500', badgeBg: 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-400' },
  { id: 'review', label: 'Under Review', color: 'bg-purple-500', badgeBg: 'bg-purple-50 text-purple-700 dark:bg-purple-950/60 dark:text-purple-400' },
  { id: 'completed', label: 'Completed', color: 'bg-emerald-500', badgeBg: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400' },
  { id: 'blocked', label: 'Blocked', color: 'bg-rose-500', badgeBg: 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400' },
];

export const KanbanBoard: React.FC<KanbanBoardProps> = () => {
  const { user } = useAuthStore();

  // Load persisted tasks or fallback to default
  const [tasks, setTasks] = useState<Task[]>(() => {
    const saved = localStorage.getItem('workos_kanban_tasks');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return DEFAULT_TASKS;
      }
    }
    return DEFAULT_TASKS;
  });

  const [draggedTaskId, setDraggedTaskId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');

  // Modals state
  const [isNewTaskModalOpen, setIsNewTaskModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [activeMenuTaskId, setActiveMenuTaskId] = useState<string | null>(null);

  // New task form fields
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newPriority, setNewPriority] = useState<TaskPriority>('medium');
  const [newStatus, setNewStatus] = useState<TaskStatus>('todo');
  const [newHours, setNewHours] = useState(16);

  // Comments for selected task
  const [taskComments, setTaskComments] = useState<Record<string, { author: string; text: string; time: string }[]>>({});
  const [newCommentText, setNewCommentText] = useState('');

  // Persist tasks whenever they change
  useEffect(() => {
    localStorage.setItem('workos_kanban_tasks', JSON.stringify(tasks));
  }, [tasks]);

  // Drag and Drop handlers
  const handleDragStart = (e: React.DragEvent, id: string) => {
    e.dataTransfer.setData('text/plain', id);
    setDraggedTaskId(id);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent, targetStatus: TaskStatus) => {
    e.preventDefault();
    const id = e.dataTransfer.getData('text/plain') || draggedTaskId;
    if (!id) return;

    moveTaskToStatus(id, targetStatus);
    setDraggedTaskId(null);
  };

  // Move task status
  const moveTaskToStatus = (taskId: string, targetStatus: TaskStatus) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, status: targetStatus } : t))
    );
    if (selectedTask && selectedTask.id === taskId) {
      setSelectedTask((prev) => prev ? { ...prev, status: targetStatus } : null);
    }
    setActiveMenuTaskId(null);
  };

  // Move to next column
  const moveTaskNext = (task: Task) => {
    const order: TaskStatus[] = ['todo', 'in_progress', 'review', 'completed'];
    const currentIndex = order.indexOf(task.status);
    if (currentIndex >= 0 && currentIndex < order.length - 1) {
      moveTaskToStatus(task.id, order[currentIndex + 1]);
    } else if (task.status === 'blocked') {
      moveTaskToStatus(task.id, 'in_progress');
    }
  };

  // Move to previous column
  const moveTaskPrev = (task: Task) => {
    const order: TaskStatus[] = ['todo', 'in_progress', 'review', 'completed'];
    const currentIndex = order.indexOf(task.status);
    if (currentIndex > 0) {
      moveTaskToStatus(task.id, order[currentIndex - 1]);
    }
  };

  // Delete task
  const deleteTask = (taskId: string) => {
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
    if (selectedTask?.id === taskId) {
      setSelectedTask(null);
    }
    setActiveMenuTaskId(null);
  };

  // Create new task submit
  const handleCreateTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    const newTask: Task = {
      id: 't-' + Math.random().toString(36).substring(2, 7),
      workspace_id: 'ws-1',
      project_id: 'p-1',
      title: newTitle.trim(),
      description: newDesc.trim() || undefined,
      status: newStatus,
      priority: newPriority,
      estimated_hours: Number(newHours) || 8,
      actual_hours: 0,
      created_at: new Date().toISOString().split('T')[0],
      dependency_ids: [],
    };

    setTasks((prev) => [newTask, ...prev]);
    setNewTitle('');
    setNewDesc('');
    setNewPriority('medium');
    setNewStatus('todo');
    setNewHours(16);
    setIsNewTaskModalOpen(false);
  };

  // Add comment to task
  const handleAddComment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTask || !newCommentText.trim()) return;

    const authorName = user?.full_name || 'Sarah Connor';
    const commentObj = {
      author: authorName,
      text: newCommentText.trim(),
      time: 'Just now',
    };

    setTaskComments((prev) => ({
      ...prev,
      [selectedTask.id]: [...(prev[selectedTask.id] || []), commentObj],
    }));

    setNewCommentText('');
  };

  const getPriorityBadge = (priority: TaskPriority) => {
    switch (priority) {
      case 'urgent':
        return <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400">URGENT</span>;
      case 'high':
        return <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400">HIGH</span>;
      case 'medium':
        return <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-400">MED</span>;
      default:
        return <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400">LOW</span>;
    }
  };

  const userInitial = (user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U').toUpperCase();

  // Filter tasks
  const filteredTasks = tasks.filter((t) => {
    const matchesSearch = t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (t.description && t.description.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesPriority = priorityFilter === 'all' || t.priority === priorityFilter;
    return matchesSearch && matchesPriority;
  });

  return (
    <div className="h-full flex flex-col space-y-4">
      {/* Top Header & Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-200/80 dark:border-slate-800">
        <div>
          <h1 className="text-xl font-bold tracking-tight">Project Task Board</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Sprint Execution • Click card to edit, or drag to update status
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          {/* Quick Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1.5 text-xs rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 w-36 sm:w-48"
            />
          </div>

          {/* Priority Filter */}
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="text-xs py-1.5 px-2 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 focus:outline-none"
          >
            <option value="all">All Priorities</option>
            <option value="urgent">Urgent</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          {/* Add Task Button */}
          <button
            onClick={() => setIsNewTaskModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm transition cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Task</span>
          </button>
        </div>
      </div>

      {/* Kanban Columns Grid */}
      <div className="flex-1 grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 overflow-x-auto pb-4">
        {COLUMNS.map((col) => {
          const colTasks = filteredTasks.filter((t) => t.status === col.id);
          return (
            <div
              key={col.id}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, col.id)}
              className="bg-slate-100/70 dark:bg-slate-900/40 rounded-xl p-3 flex flex-col min-w-[240px] border border-slate-200/60 dark:border-slate-800"
            >
              {/* Column Header */}
              <div className="flex items-center justify-between pb-3 px-1 border-b border-slate-200/50 dark:border-slate-800 mb-3">
                <div className="flex items-center gap-2">
                  <span className={`w-2.5 h-2.5 rounded-full ${col.color}`} />
                  <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{col.label}</span>
                </div>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 shadow-2xs">
                  {colTasks.length}
                </span>
              </div>

              {/* Task Cards List */}
              <div className="flex-1 space-y-2.5 overflow-y-auto">
                {colTasks.length === 0 ? (
                  <div className="h-28 flex flex-col items-center justify-center border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-lg text-slate-400 text-xs">
                    <span>No tasks</span>
                    <button
                      onClick={() => {
                        setNewStatus(col.id);
                        setIsNewTaskModalOpen(true);
                      }}
                      className="mt-1 text-[11px] text-indigo-600 dark:text-indigo-400 hover:underline inline-flex items-center gap-0.5"
                    >
                      <Plus className="w-3 h-3" /> Add task
                    </button>
                  </div>
                ) : (
                  colTasks.map((task) => (
                    <div
                      key={task.id}
                      draggable
                      onDragStart={(e) => handleDragStart(e, task.id)}
                      onClick={() => setSelectedTask(task)}
                      className="group p-3.5 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-lg shadow-2xs hover:shadow-md hover:border-indigo-500/50 cursor-pointer transition relative"
                    >
                      {/* Priority and Options Header */}
                      <div className="flex items-start justify-between gap-2">
                        {getPriorityBadge(task.priority)}

                        <div className="relative" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => setActiveMenuTaskId(activeMenuTaskId === task.id ? null : task.id)}
                            className="p-1 rounded text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
                          >
                            <MoreVertical className="w-3.5 h-3.5" />
                          </button>

                          {/* 3-Dots Dropdown Menu */}
                          {activeMenuTaskId === task.id && (
                            <div className="absolute right-0 top-6 w-36 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg py-1 z-30 text-xs">
                              <button
                                onClick={() => {
                                  setSelectedTask(task);
                                  setActiveMenuTaskId(null);
                                }}
                                className="w-full px-3 py-1.5 text-left text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center gap-2"
                              >
                                <Edit2 className="w-3.5 h-3.5" /> Edit Details
                              </button>
                              <button
                                onClick={() => moveTaskNext(task)}
                                className="w-full px-3 py-1.5 text-left text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center gap-2"
                              >
                                <ArrowRight className="w-3.5 h-3.5" /> Move Next
                              </button>
                              <button
                                onClick={() => deleteTask(task.id)}
                                className="w-full px-3 py-1.5 text-left text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 flex items-center gap-2"
                              >
                                <Trash2 className="w-3.5 h-3.5" /> Delete
                              </button>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Title */}
                      <h4 className="text-xs font-semibold mt-2 text-slate-900 dark:text-slate-100 leading-snug group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                        {task.title}
                      </h4>

                      {/* Description */}
                      {task.description && (
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                          {task.description}
                        </p>
                      )}

                      {/* Card Footer: Dependencies, Hours & Dynamic User Avatar */}
                      <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
                        <div className="flex items-center gap-2.5">
                          {task.dependency_ids && task.dependency_ids.length > 0 && (
                            <div className="flex items-center gap-1 text-indigo-600 dark:text-indigo-400 font-mono text-[10px]" title="Dependencies">
                              <GitBranch className="w-3 h-3" />
                              <span>{task.dependency_ids.length}</span>
                            </div>
                          )}
                          <div className="flex items-center gap-1 text-slate-400 text-[10px]">
                            <Clock className="w-3 h-3" />
                            <span>{task.estimated_hours}h</span>
                          </div>
                        </div>

                        {/* Interactive Avatar using User Profile */}
                        <div
                          className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-[9px] shadow-2xs"
                          title={user?.full_name || 'Assigned Member'}
                        >
                          {userInitial}
                        </div>
                      </div>

                      {/* Quick Move Buttons visible on hover */}
                      <div className="mt-2 pt-1 border-t border-slate-100 dark:border-slate-800/60 hidden group-hover:flex items-center justify-between text-[10px] text-slate-400">
                        {col.id !== 'todo' ? (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              moveTaskPrev(task);
                            }}
                            className="hover:text-indigo-600 flex items-center gap-0.5"
                          >
                            <ArrowLeft className="w-3 h-3" /> Back
                          </button>
                        ) : <span />}

                        {col.id !== 'completed' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              moveTaskNext(task);
                            }}
                            className="hover:text-indigo-600 flex items-center gap-0.5 ml-auto font-medium"
                          >
                            Next <ArrowRight className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* ========================================================================= */}
      {/* MODAL 1: CREATE NEW TASK MODAL */}
      {/* ========================================================================= */}
      {isNewTaskModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl relative animate-in fade-in duration-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <Plus className="w-4 h-4 text-indigo-600" />
                Create New Project Task
              </h2>
              <button
                onClick={() => setIsNewTaskModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateTask} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Task Title *
                </label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Implement Stripe Webhook Listener"
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Description
                </label>
                <textarea
                  rows={3}
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Describe task requirements, deliverables, and acceptance criteria..."
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                    Priority
                  </label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value as TaskPriority)}
                    className="w-full px-2.5 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                    Initial Status
                  </label>
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value as TaskStatus)}
                    className="w-full px-2.5 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
                  >
                    <option value="todo">To Do</option>
                    <option value="in_progress">In Progress</option>
                    <option value="review">Review</option>
                    <option value="completed">Completed</option>
                    <option value="blocked">Blocked</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                    Est. Hours
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="160"
                    value={newHours}
                    onChange={(e) => setNewHours(Number(e.target.value))}
                    className="w-full px-2.5 py-2 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsNewTaskModalOpen(false)}
                  className="px-4 py-2 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-sm transition"
                >
                  Create Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 2: TASK DETAIL & EDIT MODAL */}
      {/* ========================================================================= */}
      {selectedTask && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl w-full max-w-xl p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-start justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-bold">
                  {selectedTask.id}
                </span>
                {getPriorityBadge(selectedTask.priority)}
              </div>
              <button
                onClick={() => setSelectedTask(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Task Info Body */}
            <div className="mt-4 space-y-4">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  {selectedTask.title}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                  {selectedTask.description || 'No detailed description provided.'}
                </p>
              </div>

              {/* Status Mover Quick Buttons */}
              <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200/80 dark:border-slate-700/80">
                <span className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-2">
                  Change Task Status:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {COLUMNS.map((col) => (
                    <button
                      key={col.id}
                      onClick={() => moveTaskToStatus(selectedTask.id, col.id)}
                      className={`px-3 py-1 text-xs font-semibold rounded-lg transition ${
                        selectedTask.status === col.id
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-100'
                      }`}
                    >
                      {col.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Meta Grid */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
                  <span className="text-slate-400 text-[10px] uppercase font-bold">Estimated Effort</span>
                  <p className="font-semibold mt-0.5">{selectedTask.estimated_hours} Hours</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800">
                  <span className="text-slate-400 text-[10px] uppercase font-bold">Assigned Engineer</span>
                  <p className="font-semibold mt-0.5">{user?.full_name || 'Sarah Connor'}</p>
                </div>
              </div>

              {/* Comments Section */}
              <div className="pt-2 border-t border-slate-100 dark:border-slate-800 space-y-3">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <MessageSquare className="w-3.5 h-3.5 text-indigo-500" />
                  Task Discussion & Activity
                </span>

                <div className="space-y-2 max-h-36 overflow-y-auto">
                  {(taskComments[selectedTask.id] || [
                    { author: 'System', text: 'Task initialized in workspace sprint graph.', time: 'Initial' }
                  ]).map((c, i) => (
                    <div key={i} className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 text-xs">
                      <div className="flex items-center justify-between text-[10px] text-slate-400 font-medium">
                        <span>{c.author}</span>
                        <span>{c.time}</span>
                      </div>
                      <p className="text-slate-800 dark:text-slate-200 mt-1">{c.text}</p>
                    </div>
                  ))}
                </div>

                {/* Comment Input */}
                <form onSubmit={handleAddComment} className="flex gap-2">
                  <input
                    type="text"
                    value={newCommentText}
                    onChange={(e) => setNewCommentText(e.target.value)}
                    placeholder="Write a comment or status update..."
                    className="flex-1 px-3 py-1.5 text-xs rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                  <button
                    type="submit"
                    className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold transition"
                  >
                    Post
                  </button>
                </form>
              </div>

              {/* Modal Footer */}
              <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => deleteTask(selectedTask.id)}
                  className="px-3 py-1.5 text-xs font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-xl flex items-center gap-1.5 transition"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  Delete Task
                </button>

                <button
                  type="button"
                  onClick={() => setSelectedTask(null)}
                  className="px-4 py-1.5 text-xs font-semibold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-200 rounded-xl"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
