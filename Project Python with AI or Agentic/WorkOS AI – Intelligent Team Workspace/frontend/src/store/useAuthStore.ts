import { create } from 'zustand';
import { User } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  login: (userData: User, token: string) => void;
  logout: () => void;
}

const savedUserRaw = localStorage.getItem('user_data');
let initialUser: User | null = null;
try {
  initialUser = savedUserRaw ? JSON.parse(savedUserRaw) : null;
} catch (e) {
  initialUser = null;
}

const savedToken = localStorage.getItem('access_token');

export const useAuthStore = create<AuthState>((set) => ({
  user: initialUser,
  token: savedToken,
  isAuthenticated: !!savedToken && !!initialUser,
  setUser: (user) => {
    if (user) {
      localStorage.setItem('user_data', JSON.stringify(user));
    } else {
      localStorage.removeItem('user_data');
    }
    set({ user, isAuthenticated: !!user });
  },
  setToken: (token) => {
    if (token) {
      localStorage.setItem('access_token', token);
      set({ token, isAuthenticated: true });
    } else {
      localStorage.removeItem('access_token');
      set({ token: null, isAuthenticated: false, user: null });
    }
  },
  login: (userData, token) => {
    localStorage.setItem('access_token', token);
    localStorage.setItem('user_data', JSON.stringify(userData));
    set({
      user: userData,
      token,
      isAuthenticated: true,
    });
  },
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('active_workspace_id');
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },
}));
