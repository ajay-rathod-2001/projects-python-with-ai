import { create } from 'zustand';
import { Workspace } from '../types';

interface WorkspaceState {
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  setWorkspaces: (workspaces: Workspace[]) => void;
  setActiveWorkspace: (workspace: Workspace) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  workspaces: [],
  activeWorkspace: null,
  setWorkspaces: (workspaces) => {
    set({ workspaces });
    const savedId = localStorage.getItem('active_workspace_id');
    const matched = workspaces.find((w) => w.id === savedId) || workspaces[0] || null;
    if (matched) {
      localStorage.setItem('active_workspace_id', matched.id);
      set({ activeWorkspace: matched });
    }
  },
  setActiveWorkspace: (workspace) => {
    localStorage.setItem('active_workspace_id', workspace.id);
    set({ activeWorkspace: workspace });
  },
}));

