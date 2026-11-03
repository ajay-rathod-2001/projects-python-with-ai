export type UserRole = 'owner' | 'admin' | 'member' | 'viewer';

export interface User {
  id: string;
  email: string;
  username?: string;
  mobile?: string;
  full_name: string;
  avatar_url?: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
  settings: Record<string, any>;
  created_at: string;
}

export interface WorkspaceMember {
  id: string;
  workspace_id: string;
  user_id: string;
  role: UserRole;
  joined_at: string;
  user?: User;
}

export type ProjectStatus = 'planning' | 'active' | 'on_hold' | 'completed' | 'archived';

export interface Project {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  status: ProjectStatus;
  start_date?: string;
  target_date?: string;
  lead_id?: string;
  created_at: string;
  lead?: User;
}

export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'completed' | 'blocked';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Task {
  id: string;
  workspace_id: string;
  project_id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee_id?: string;
  due_date?: string;
  estimated_hours: number;
  actual_hours: number;
  created_at: string;
  assignee?: User;
  dependency_ids?: string[];
}

export interface PlannedTask {
  temp_id: string;
  title: string;
  description: string;
  priority: string;
  estimated_hours: number;
  role_suggestion?: string;
  depends_on: string[];
}

export interface PlannedMilestone {
  title: string;
  week_number: number;
  tasks: PlannedTask[];
}

export interface GeneratedPlan {
  project_name: string;
  summary: string;
  suggested_timeline_weeks: number;
  milestones: PlannedMilestone[];
  identified_risks: string[];
  suggested_team_roles: string[];
}

export interface StagedPlanResponse {
  action_audit_id: string;
  status: string;
  plan: GeneratedPlan;
  message: string;
}

export interface Meeting {
  id: string;
  workspace_id: string;
  project_id?: string;
  title: string;
  summary?: string;
  key_decisions: string[];
  created_at: string;
  action_items?: MeetingActionItem[];
}

export interface MeetingActionItem {
  id: string;
  meeting_id: string;
  action_text: string;
  suggested_assignee_id?: string;
  suggested_due_date?: string;
  status: 'pending' | 'approved' | 'rejected' | 'converted';
  converted_task_id?: string;
  suggested_assignee?: User;
}
