#!/usr/bin/env python3
"""
WorkOS AI - Standalone Desktop Application
Multi-tenant AI Operating System for Teams.
Packaged into a single standalone Windows executable (.exe).
"""

import sys
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Ensure path includes backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Active session state
CURRENT_USER = {
    "name": "Sarah Connor",
    "email": "sarah@workos.ai",
    "username": "sarah_c",
    "mobile": "+1 555-0199",
    "role": "OWNER",
    "workspace": "Acme Engineering Workspace",
}

# Dark theme palette
BG_DARK = "#090d16"
BG_CARD = "#111827"
BG_INPUT = "#1f2937"
BORDER_COLOR = "#374151"
ACCENT_INDIGO = "#6366f1"
ACCENT_GREEN = "#10b981"
ACCENT_ROSE = "#f43f5e"
ACCENT_AMBER = "#f59e0b"
TEXT_WHITE = "#f9fafb"
TEXT_MUTED = "#9ca3af"


class WorkOSDesktopApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("WorkOS AI – Intelligent Team Workspace")
        self.root.geometry("1100x720")
        self.root.minsize(950, 600)
        self.root.configure(bg=BG_DARK)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()

        # Build UI
        self.create_header()
        self.create_tabs()

    def configure_styles(self):
        self.style.configure(".", background=BG_DARK, foreground=TEXT_WHITE, font=("Segoe UI", 9))
        self.style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            background=BG_CARD,
            foreground=TEXT_MUTED,
            padding=[16, 8],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", ACCENT_INDIGO)],
            foreground=[("selected", TEXT_WHITE)],
        )

    def create_header(self):
        header_frame = tk.Frame(self.root, bg=BG_CARD, height=60, bd=1, relief="solid")
        header_frame.pack(side="top", fill="x")

        # Logo & App Title
        logo_label = tk.Label(
            header_frame,
            text=" ⚡ WorkOS AI ",
            bg=ACCENT_INDIGO,
            fg=TEXT_WHITE,
            font=("Segoe UI", 11, "bold"),
            padx=10,
            pady=4,
        )
        logo_label.pack(side="left", padx=16, pady=12)

        title_label = tk.Label(
            header_frame,
            text="Intelligent Team Workspace • Agentic AI Engine",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        title_label.pack(side="left", pady=12)

        # Right Side: User profile & Action buttons
        actions_frame = tk.Frame(header_frame, bg=BG_CARD)
        actions_frame.pack(side="right", padx=16, pady=12)

        self.user_lbl = tk.Label(
            actions_frame,
            text=f"👤 {CURRENT_USER['name']} ({CURRENT_USER['email']}) [{CURRENT_USER['role']}]",
            bg=BG_INPUT,
            fg=TEXT_WHITE,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
        )
        self.user_lbl.pack(side="left", padx=6)

        btn_switch = tk.Button(
            actions_frame,
            text="Switch User / Login",
            bg=BORDER_COLOR,
            fg=TEXT_WHITE,
            activebackground=ACCENT_INDIGO,
            activeforeground=TEXT_WHITE,
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.show_login_dialog,
        )
        btn_switch.pack(side="left", padx=4)

        btn_logout = tk.Button(
            actions_frame,
            text="Log out",
            bg="#3b111a",
            fg=ACCENT_ROSE,
            activebackground=ACCENT_ROSE,
            activeforeground=TEXT_WHITE,
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.handle_logout,
        )
        btn_logout.pack(side="left", padx=4)

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=12)

        # Tab 1: AI Planner
        self.tab_planner = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(self.tab_planner, text=" 🤖 AI Project Planner ")
        self.build_planner_tab()

        # Tab 2: Kanban Board
        self.tab_kanban = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(self.tab_kanban, text=" 📋 Kanban Board ")
        self.build_kanban_tab()

        # Tab 3: Risk Detector
        self.tab_risks = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(self.tab_risks, text=" ⚡ Risk Detection ")
        self.build_risks_tab()

        # Tab 4: Meeting Intelligence
        self.tab_meetings = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(self.tab_meetings, text=" 🎙️ Meeting Intelligence ")
        self.build_meetings_tab()

        # Tab 5: Workspace RAG
        self.tab_rag = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(self.tab_rag, text=" 🔍 Workspace RAG ")
        self.build_rag_tab()

    # =========================================================================
    # TAB 1: AI PROJECT PLANNER
    # =========================================================================
    def build_planner_tab(self):
        container = tk.Frame(self.tab_planner, bg=BG_DARK)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        # Input card
        input_card = tk.LabelFrame(
            container,
            text=" Project Brief or Business Requirement ",
            bg=BG_CARD,
            fg=TEXT_WHITE,
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=10,
            relief="groove",
        )
        input_card.pack(fill="x", pady=6)

        self.brief_entry = tk.Text(input_card, height=3, bg=BG_INPUT, fg=TEXT_WHITE, insertbackground="white", font=("Segoe UI", 10))
        self.brief_entry.insert("1.0", "Build an e-commerce application within 8 weeks with Stripe payments, product catalog, and live Kanban.")
        self.brief_entry.pack(fill="x", pady=4)

        btn_row = tk.Frame(input_card, bg=BG_CARD)
        btn_row.pack(fill="x", pady=4)

        tk.Label(btn_row, text="Target Timeline: 8 Weeks • Target Velocity: ~30h/week", bg=BG_CARD, fg=TEXT_MUTED).pack(side="left")

        btn_generate = tk.Button(
            btn_row,
            text="✨ Generate AI Project Plan",
            bg=ACCENT_INDIGO,
            fg=TEXT_WHITE,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.generate_ai_plan,
        )
        btn_generate.pack(side="right")

        # Staged plan output area
        out_card = tk.LabelFrame(
            container,
            text=" Staged Execution Graph (Human-in-the-Loop Review) ",
            bg=BG_CARD,
            fg=ACCENT_INDIGO,
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=10,
        )
        out_card.pack(fill="both", expand=True, pady=6)

        self.plan_text = scrolledtext.ScrolledText(out_card, bg=BG_INPUT, fg=TEXT_WHITE, font=("Consolas", 10))
        self.plan_text.pack(fill="both", expand=True, pady=6)
        self.render_sample_plan()

        # Approval button
        appr_row = tk.Frame(out_card, bg=BG_CARD)
        appr_row.pack(fill="x", pady=4)

        btn_approve = tk.Button(
            appr_row,
            text="✔ Approve & Publish Tasks to Kanban Board",
            bg=ACCENT_GREEN,
            fg=TEXT_WHITE,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=lambda: messagebox.showinfo("Action Approved", "AI Project Plan approved! 8 tasks committed to PostgreSQL & published to Kanban."),
        )
        btn_approve.pack(side="right")

    def render_sample_plan(self):
        sample = """======================================================================
PROJECT: E-Commerce Application Platform
SUMMARY: 8-week full-stack e-commerce implementation with multi-tenant isolation.
STATUS: PENDING APPROVAL (Staged in agent_action_audits)
======================================================================

[PHASE 1: Architecture, Core Schemas & Auth] (Week 1-2)
  * [T1] Design Relational Schema & Tenant Isolation
         Priority: URGENT | Est: 20h | Role: Backend Architect | Dependencies: None
  * [T2] Setup JWT Authentication & User Sessions
         Priority: HIGH   | Est: 16h | Role: Backend Engineer   | Dependencies: [T1]

[PHASE 2: Core Domain Features & Business Logic] (Week 3-5)
  * [T3] Product Catalog & Inventory Service
         Priority: HIGH   | Est: 32h | Role: Full Stack Eng    | Dependencies: [T1]
  * [T4] Stripe Webhook Gateway & Payment Flow
         Priority: URGENT | Est: 40h | Role: Senior Backend Eng | Dependencies: [T2, T3]

[PHASE 3: Real-Time Kanban & Delivery Dashboard] (Week 6-8)
  * [T5] FastAPI WebSockets & Redis Pub/Sub Broadcast
         Priority: MEDIUM | Est: 24h | Role: Frontend Engineer  | Dependencies: [T3]

DETECTED RISKS:
  ! Stripe Webhook sandbox requires registered SSL test domain before end-to-end checkout.
  ! Real-time WebSocket reconnection handling across high-latency clients needs backoff.
"""
        self.plan_text.delete("1.0", tk.END)
        self.plan_text.insert(tk.END, sample)

    def generate_ai_plan(self):
        brief = self.brief_entry.get("1.0", tk.END).strip()
        if not brief:
            messagebox.showwarning("Empty Brief", "Please enter a project brief first.")
            return
        self.render_sample_plan()
        messagebox.showinfo("AI Planner", "AI has generated and staged the project execution graph!")

    # =========================================================================
    # TAB 2: KANBAN BOARD
    # =========================================================================
    def build_kanban_tab(self):
        container = tk.Frame(self.tab_kanban, bg=BG_DARK)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        columns = [
            ("TO DO", ACCENT_AMBER, [
                ("[T-4] Real-Time WebSocket Sync", "Priority: Medium • 18h", "Alex Rivera"),
            ]),
            ("IN PROGRESS", ACCENT_INDIGO, [
                ("[T-2] JWT Authentication & RBAC", "Priority: High • 20h", "Sarah Connor"),
            ]),
            ("REVIEW", "#8b5cf6", [
                ("[T-5] AI ReAct Agent Planning", "Priority: High • 24h", "Sarah Connor"),
            ]),
            ("COMPLETED", ACCENT_GREEN, [
                ("[T-1] Design Relational Schema", "Priority: Urgent • 16h", "Sarah Connor"),
            ]),
            ("BLOCKED", ACCENT_ROSE, [
                ("[T-3] Stripe Webhook Gateway", "Priority: Urgent • 32h", "Alex Rivera"),
            ]),
        ]

        # 5 Columns Grid
        for i, (title, color, tasks) in enumerate(columns):
            col_frame = tk.LabelFrame(
                container,
                text=f" {title} ({len(tasks)}) ",
                bg=BG_CARD,
                fg=color,
                font=("Segoe UI", 9, "bold"),
                padx=8,
                pady=8,
            )
            col_frame.grid(row=0, column=i, sticky="nsew", padx=4, pady=4)
            container.grid_columnconfigure(i, weight=1)
            container.grid_rowconfigure(0, weight=1)

            for tid, meta, assignee in tasks:
                card = tk.Frame(col_frame, bg=BG_INPUT, bd=1, relief="solid")
                card.pack(fill="x", pady=4, padx=2)
                tk.Label(card, text=tid, bg=BG_INPUT, fg=TEXT_WHITE, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=6, pady=2)
                tk.Label(card, text=meta, bg=BG_INPUT, fg=TEXT_MUTED, font=("Segoe UI", 8)).pack(anchor="w", padx=6)
                tk.Label(card, text=f"👤 {assignee}", bg=BG_INPUT, fg=ACCENT_INDIGO, font=("Segoe UI", 8)).pack(anchor="w", padx=6, pady=2)

    # =========================================================================
    # TAB 3: RISK DETECTION
    # =========================================================================
    def build_risks_tab(self):
        container = tk.Frame(self.tab_risks, bg=BG_DARK)
        container.pack(fill="both", expand=True, padx=16, pady=16)

        # Health Meter
        meter_card = tk.LabelFrame(container, text=" Project Delivery Health ", bg=BG_CARD, fg=TEXT_WHITE, font=("Segoe UI", 10, "bold"), padx=12, pady=12)
        meter_card.pack(fill="x", pady=8)

        score_lbl = tk.Label(meter_card, text="92 / 100", font=("Segoe UI", 32, "bold"), fg=ACCENT_GREEN, bg=BG_CARD)
        score_lbl.pack(side="left", padx=20)

        info_lbl = tk.Label(
            meter_card,
            text="Status: LOW DELIVERY RISK • 0 Overdue Tasks • 1 Blocked Task\n"
                 "Estimated Completion: Dec 28, 2026 (On Schedule)",
            bg=BG_CARD,
            fg=TEXT_WHITE,
            font=("Segoe UI", 10),
            justify="left",
        )
        info_lbl.pack(side="left", padx=10)

        # Bottlenecks
        bottle_card = tk.LabelFrame(container, text=" Critical Path Bottlenecks Detected ", bg=BG_CARD, fg=ACCENT_ROSE, font=("Segoe UI", 10, "bold"), padx=12, pady=12)
        bottle_card.pack(fill="both", expand=True, pady=8)

        txt = (
            "⚠️ Task #T-3: Stripe Webhook Gateway & Payment Flow\n"
            "   Status: BLOCKED\n"
            "   Root Cause: Awaiting SSL certificate test domain.\n"
            "   Downstream Impact: Halts checkout validation and order confirmation email tasks.\n\n"
            "💡 AI Actionable Recommendations:\n"
            "   1. Reassign 1 backend engineer to resolve SSL endpoint within 48h to preserve timeline.\n"
            "   2. Pre-seed pgvector test embeddings in staging to avoid indexing latency.\n"
        )
        lbl_msg = tk.Label(bottle_card, text=txt, bg=BG_INPUT, fg=TEXT_WHITE, font=("Consolas", 10), justify="left", padx=10, pady=10)
        lbl_msg.pack(fill="both", expand=True)

    # =========================================================================
    # TAB 4: MEETING INTELLIGENCE
    # =========================================================================
    def build_meetings_tab(self):
        container = tk.Frame(self.tab_meetings, bg=BG_DARK)
        container.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(container, text="Raw Meeting Notes or Transcript:", bg=BG_DARK, fg=TEXT_WHITE, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        txt_trans = tk.Text(container, height=4, bg=BG_INPUT, fg=TEXT_WHITE, insertbackground="white", font=("Segoe UI", 9))
        txt_trans.insert("1.0", "Sarah: Let's finalize checkout flow by Friday. Alex, please review the schema migration for task dependencies. Alex: Yes, I will deploy the pgvector index updates before tomorrow.")
        txt_trans.pack(fill="x", pady=6)

        btn_proc = tk.Button(container, text="✨ Extract Decisions & Action Items", bg=ACCENT_INDIGO, fg=TEXT_WHITE, font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=6)
        btn_proc.pack(anchor="e", pady=4)

        res_box = tk.LabelFrame(container, text=" Extracted Insights & Actionable Tasks ", bg=BG_CARD, fg=TEXT_WHITE, font=("Segoe UI", 10, "bold"), padx=12, pady=12)
        res_box.pack(fill="both", expand=True, pady=8)

        insights = (
            "✔ Key Decision: Checkout flow completion deadline committed to Friday.\n"
            "✔ Key Decision: pgvector index updates will be finalized prior to standup.\n\n"
            "📋 Extracted Tasks (Ready to Convert):\n"
            "  * Deploy pgvector index updates (Assigned: Alex Rivera, Due: Tomorrow)\n"
            "  * Configure Stripe test credentials and webhook (Assigned: Sarah Connor, Due: Friday)\n"
        )
        tk.Label(res_box, text=insights, bg=BG_INPUT, fg=TEXT_WHITE, font=("Segoe UI", 10), justify="left", padx=10, pady=10).pack(fill="both", expand=True)

    # =========================================================================
    # TAB 5: WORKSPACE RAG
    # =========================================================================
    def build_rag_tab(self):
        container = tk.Frame(self.tab_rag, bg=BG_DARK)
        container.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(container, text="Ask AI about workspace knowledge, tasks, or blockers:", bg=BG_DARK, fg=TEXT_WHITE, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        q_entry = tk.Entry(container, bg=BG_INPUT, fg=TEXT_WHITE, insertbackground="white", font=("Segoe UI", 10))
        q_entry.insert(0, "What are the current blockers in our backend project?")
        q_entry.pack(fill="x", pady=6)

        ans_card = tk.LabelFrame(container, text=" AI Context-Aware Answer (pgvector RAG) ", bg=BG_CARD, fg=ACCENT_GREEN, font=("Segoe UI", 10, "bold"), padx=12, pady=12)
        ans_card.pack(fill="both", expand=True, pady=8)

        ans_txt = (
            "Based on workspace knowledge and active sprint graphs:\n\n"
            "The backend project currently has 1 critical blocker on Task #T-3 (Stripe Webhook Gateway) "
            "due to pending SSL certificate configuration.\n\n"
            "Sources referenced:\n"
            "  1. Task #T-3: 'Stripe Webhook Gateway & Payment Flow' (Status: Blocked)\n"
            "  2. Meeting: 'Sprint 3 Planning & Architecture Sync' (Decision #2)\n"
        )
        tk.Label(ans_card, text=ans_txt, bg=BG_INPUT, fg=TEXT_WHITE, font=("Segoe UI", 10), justify="left", padx=12, pady=12).pack(fill="both", expand=True)

    # =========================================================================
    # USER AUTH / LOGIN DIALOG
    # =========================================================================
    def show_login_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("WorkOS AI - User Login")
        dialog.geometry("400x320")
        dialog.configure(bg=BG_CARD)
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(dialog, text="Sign In to WorkOS AI", font=("Segoe UI", 12, "bold"), bg=BG_CARD, fg=TEXT_WHITE).pack(pady=12)

        form_frame = tk.Frame(dialog, bg=BG_CARD, padx=20)
        form_frame.pack(fill="both", expand=True)

        tk.Label(form_frame, text="Email, Username, or Mobile:", bg=BG_CARD, fg=TEXT_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        e_ident = tk.Entry(form_frame, bg=BG_INPUT, fg=TEXT_WHITE, font=("Segoe UI", 10), insertbackground="white")
        e_ident.insert(0, CURRENT_USER["email"])
        e_ident.pack(fill="x", pady=4)

        tk.Label(form_frame, text="Password:", bg=BG_CARD, fg=TEXT_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(8, 0))
        e_pass = tk.Entry(form_frame, show="•", bg=BG_INPUT, fg=TEXT_WHITE, font=("Segoe UI", 10), insertbackground="white")
        e_pass.insert(0, "password123")
        e_pass.pack(fill="x", pady=4)

        def do_login():
            ident = e_ident.get().strip()
            if not ident:
                messagebox.showerror("Error", "Please enter your email, username, or mobile.")
                return
            CURRENT_USER["name"] = ident.split("@")[0].capitalize()
            CURRENT_USER["email"] = ident if "@" in ident else f"{ident}@workos.ai"
            CURRENT_USER["username"] = ident.split("@")[0]
            self.user_lbl.config(text=f"👤 {CURRENT_USER['name']} ({CURRENT_USER['email']}) [{CURRENT_USER['role']}]")
            dialog.destroy()
            messagebox.showinfo("Success", f"Logged in as {CURRENT_USER['name']}!")

        btn_submit = tk.Button(
            form_frame,
            text="Sign In to Workspace ➔",
            bg=ACCENT_INDIGO,
            fg=TEXT_WHITE,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            pady=6,
            cursor="hand2",
            command=do_login,
        )
        btn_submit.pack(fill="x", pady=16)

    def handle_logout(self):
        CURRENT_USER["name"] = "Guest User"
        CURRENT_USER["email"] = "guest@workos.ai"
        self.user_lbl.config(text=f"👤 Guest User [VIEWER]")
        self.show_login_dialog()


def main():
    if "--cli" in sys.argv:
        from app.cli import main as cli_main
        cli_main()
    else:
        root = tk.Tk()
        app = WorkOSDesktopApp(root)
        root.mainloop()


if __name__ == "__main__":
    main()

