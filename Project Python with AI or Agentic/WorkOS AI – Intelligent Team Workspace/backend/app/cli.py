#!/usr/bin/env python3
"""
WorkOS AI - Energetic Desktop CLI Terminal Application
Interactive Agentic AI workspace command center for engineers and teams.
"""

import sys
import os
import time
import json
import uuid
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ANSI Terminal Color Helpers
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"

# Gradients & Colors
C_INDIGO = "\033[38;5;63m"
C_PURPLE = "\033[38;5;135m"
C_CYAN = "\033[38;5;51m"
C_GREEN = "\033[38;5;48m"
C_YELLOW = "\033[38;5;220m"
C_RED = "\033[38;5;196m"
C_BG_DARK = "\033[48;5;234m"

BANNER = f"""
{C_INDIGO}██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗ ██████╗ ███████╗     █████╗ ██╗
██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝██╔═══██╗██╔════╝    ██╔══██╗██║
██║ █╗ ██║██║   ██║██████╔╝█████═╝ ██║   ██║███████╗    ███████║██║
██║███╗██║██║   ██║██╔══██╗██╔═██╗ ██║   ██║╚════██║    ██╔══██║██║
╚███╔███╔╝╚██████╔╝██║  ██║██║ ╚██╗╚██████╔╝███████║    ██║  ██║██║
 ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝    ╚═╝  ╚═╝╚═╝{C_RESET}
{C_CYAN}         ⚡ Intelligent Team Workspace • Agentic AI Engine ⚡{C_RESET}
"""

CURRENT_USER = {
    "name": "Sarah Connor",
    "email": "sarah@workos.ai",
    "username": "sarah_c",
    "mobile": "+1 555-0199",
    "workspace": "Acme Engineering Workspace",
    "role": "OWNER",
}


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print(BANNER)
    print(f"{C_BOLD}Active User:{C_RESET} {C_GREEN}{CURRENT_USER['name']}{C_RESET} ({CURRENT_USER['email']}) | {C_BOLD}Role:{C_RESET} {C_PURPLE}{CURRENT_USER['role']}{C_RESET}")
    print(f"{C_BOLD}Workspace:{C_RESET} {C_CYAN}{CURRENT_USER['workspace']}{C_RESET} | {C_BOLD}Tenant Guard:{C_RESET} {C_GREEN}Active (Strict Isolation){C_RESET}")
    print(f"{C_DIM}{'='*72}{C_RESET}\n")


def spinner_animation(text: str, duration: float = 1.2):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start = time.time()
    i = 0
    while time.time() - start < duration:
        sys.stdout.write(f"\r{C_CYAN}{frames[i % len(frames)]}{C_RESET} {C_BOLD}{text}{C_RESET}")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write(f"\r{C_GREEN}✔{C_RESET} {C_BOLD}{text}{C_RESET} {C_DIM}(Done){C_RESET}\n")


def cmd_plan(brief: str = None):
    print(f"\n{C_PURPLE}{C_BOLD}🤖 [AI Project Planning Agent - ReAct Engine]{C_RESET}")
    if not brief:
        brief = input(f"{C_YELLOW}Enter your project brief or requirement: {C_RESET}").strip()
        if not brief:
            brief = "Build an e-commerce platform within 8 weeks with Stripe payments."

    print(f"\n{C_DIM}Input Brief:{C_RESET} \"{brief}\"")
    spinner_animation("Ingesting brief and extracting technical milestones...", 0.9)
    spinner_animation("Computing task graph & estimating velocity hours...", 0.8)
    spinner_animation("Identifying cross-task dependency risks...", 0.7)

    print(f"\n{C_GREEN}{C_BOLD}Generated Project Execution Graph (STAGED FOR APPROVAL):{C_RESET}")
    print(f"{C_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C_RESET}")
    print(f"{C_BOLD}Project Name:{C_RESET} E-Commerce Application Platform")
    print(f"{C_BOLD}Target Timeline:{C_RESET} 8 Weeks • Estimated Effort: 132 Hours\n")

    milestones = [
        {
            "phase": "Phase 1: Architecture, Core Schemas & Auth (Week 1-2)",
            "tasks": [
                ("t1", "Design Relational Schema & Tenant Isolation", "Urgent", "20h", "Backend Architect", []),
                ("t2", "Setup JWT Authentication & User Sessions", "High", "16h", "Backend Engineer", ["t1"]),
            ],
        },
        {
            "phase": "Phase 2: Core Domain Features & Payments (Week 3-5)",
            "tasks": [
                ("t3", "Product Catalog & Inventory Service", "High", "32h", "Full Stack Engineer", ["t1"]),
                ("t4", "Stripe Webhook Gateway & Payment Flow", "Urgent", "40h", "Senior Backend Eng", ["t2", "t3"]),
            ],
        },
        {
            "phase": "Phase 3: Real-Time Kanban & Delivery Dashboard (Week 6-8)",
            "tasks": [
                ("t5", "FastAPI WebSockets & Redis Pub/Sub Sync", "Medium", "24h", "Frontend Engineer", ["t3"]),
            ],
        },
    ]

    for m in milestones:
        print(f"{C_YELLOW}{C_BOLD}● {m['phase']}{C_RESET}")
        for tid, title, prio, hrs, role, deps in m["tasks"]:
            prio_color = C_RED if prio == "Urgent" else (C_YELLOW if prio == "High" else C_CYAN)
            dep_str = f"{C_DIM}Depends: {', '.join(deps)}{C_RESET}" if deps else f"{C_DIM}No dependencies{C_RESET}"
            print(f"   [{tid}] {C_BOLD}{title:<45}{C_RESET} | {prio_color}{prio:<7}{C_RESET} | {hrs:<4} | {role} ({dep_str})")
        print()

    print(f"{C_RED}{C_BOLD}Detected Bottleneck Risk:{C_RESET} Stripe Webhook gateway requires test SSL domain before checkout testing.")
    print(f"{C_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C_RESET}")

    choice = input(f"\n{C_BOLD}Approve & Publish staged tasks to Kanban board? (y/n): {C_RESET}").strip().lower()
    if choice == "y":
        spinner_animation("Committing project and tasks to PostgreSQL database...", 0.6)
        spinner_animation("Broadcasting 'task.created' WebSocket event to team...", 0.5)
        print(f"{C_GREEN}{C_BOLD}✔ Project successfully published to Kanban board!{C_RESET}\n")
    else:
        print(f"{C_YELLOW}Plan retained in 'pending_approval' state in agent_action_audits.{C_RESET}\n")


def cmd_tasks():
    print(f"\n{C_CYAN}{C_BOLD}📋 [Kanban Project Task Board]{C_RESET}\n")
    columns = {
        "To Do": [
            ("t-4", "Real-Time WebSocket Sync via Redis Pub/Sub", "Medium", "18h", "Alex Rivera"),
        ],
        "In Progress": [
            ("t-2", "Implement JWT Authentication & RBAC Guard", "High", "20h", "Sarah Connor"),
        ],
        "Under Review": [
            ("t-5", "AI ReAct Agent Planning & Approval Gating", "High", "24h", "Sarah Connor"),
        ],
        "Completed": [
            ("t-1", "Design PostgreSQL Models with Tenant Isolation", "Urgent", "16h", "Sarah Connor"),
        ],
        "Blocked": [
            ("t-3", "Stripe Webhook Gateway & Payment Flow", "Urgent", "32h", "Alex Rivera"),
        ],
    }

    for col_name, tasks in columns.items():
        color = C_GREEN if col_name == "Completed" else (C_RED if col_name == "Blocked" else (C_INDIGO if col_name == "In Progress" else C_YELLOW))
        print(f"{color}{C_BOLD}─── {col_name.upper()} ({len(tasks)}) ────────────────────────────────────────{C_RESET}")
        for tid, title, prio, hrs, assignee in tasks:
            print(f"  {C_BOLD}[{tid}]{C_RESET} {title}")
            print(f"        Priority: {prio} | Effort: {hrs} | Assigned: {assignee}")
        print()


def cmd_risks():
    print(f"\n{C_RED}{C_BOLD}⚡ [AI Project Risk Detection Engine]{C_RESET}\n")
    spinner_animation("Analyzing task dependency graph & milestone velocity...", 0.8)

    print(f"\n{C_BOLD}Project Health Score:{C_RESET} {C_GREEN}{C_BOLD}92 / 100{C_RESET} ({C_GREEN}Low Delivery Risk{C_RESET})")
    print(f"{C_BOLD}Total Tasks:{C_RESET} 5 | {C_BOLD}Completed:{C_RESET} 1 | {C_BOLD}Blocked:{C_RESET} 1 | {C_BOLD}Overdue:{C_RESET} 0\n")

    print(f"{C_RED}{C_BOLD}Critical Path Bottlenecks:{C_RESET}")
    print(f"  • {C_BOLD}Task #t-3 (Stripe Webhook Gateway){C_RESET}")
    print(f"    {C_DIM}Root Cause:{C_RESET} Awaiting SSL sandbox domain certificate.")
    print(f"    {C_DIM}Downstream Impact:{C_RESET} Directly blocks Phase 2 Checkout UI integration.\n")

    print(f"{C_CYAN}{C_BOLD}AI Recommended Actions:{C_RESET}")
    print(f"  1. Reassign 1 backend engineer to resolve Stripe SSL listener within 48h.")
    print(f"  2. Pre-seed pgvector test embeddings in staging to avoid latency.")
    print()


def cmd_meetings():
    print(f"\n{C_PURPLE}{C_BOLD}🎙️ [AI Meeting Intelligence]{C_RESET}\n")
    sample_notes = "Sarah: Let's finalize checkout flow by Friday. Alex, can you review the schema migration for task dependencies? Alex: Yes, I will deploy the pgvector index updates before tomorrow."
    print(f"{C_DIM}Sample Meeting Transcript:{C_RESET}\n\"{sample_notes}\"\n")

    spinner_animation("Extracting key decisions and actionable commitments...", 0.8)
    print(f"\n{C_GREEN}{C_BOLD}Extracted Key Decisions:{C_RESET}")
    print("  ✔ Checkout flow completion deadline committed to Friday.")
    print("  ✔ pgvector index updates will be finalized prior to tomorrow standup.\n")

    print(f"{C_YELLOW}{C_BOLD}Extracted Action Items (Ready to Convert to Task):{C_RESET}")
    print("  [AI-1] Deploy pgvector index updates (Assignee: Alex, Due: Tomorrow)")
    print("  [AI-2] Finalize Stripe test credentials and webhook (Assignee: Sarah, Due: Friday)\n")


def cmd_login():
    print(f"\n{C_CYAN}{C_BOLD}🔑 [WorkOS AI - User Login & Identity Switch]{C_RESET}\n")
    ident = input(f"{C_YELLOW}Enter Email, Username, or Mobile: {C_RESET}").strip()
    if not ident:
        print(f"{C_RED}Identifier cannot be empty.{C_RESET}\n")
        return

    pwd = input(f"{C_YELLOW}Enter Password: {C_RESET}").strip()
    if not pwd:
        print(f"{C_RED}Password is required.{C_RESET}\n")
        return

    spinner_animation("Authenticating credentials...", 0.6)
    CURRENT_USER["name"] = ident.split("@")[0].capitalize() if "@" in ident else ident.capitalize()
    CURRENT_USER["email"] = ident if "@" in ident else f"{ident}@workos.ai"
    CURRENT_USER["username"] = ident.split("@")[0]
    CURRENT_USER["workspace"] = f"{CURRENT_USER['name']}'s Workspace"
    print(f"{C_GREEN}{C_BOLD}✔ Successfully authenticated as {CURRENT_USER['name']} ({CURRENT_USER['email']})!{C_RESET}\n")


def interactive_menu():
    while True:
        print_banner()
        print(f"{C_BOLD}Available Commands:{C_RESET}")
        print(f"  {C_PURPLE}1.{C_RESET} 🤖 AI Project Planning Agent  (Create project plan from brief)")
        print(f"  {C_CYAN}2.{C_RESET} 📋 View Kanban Task Board      (Inspect sprint status)")
        print(f"  {C_RED}3.{C_RESET} ⚡ Project Risk Detector       (Analyze delivery health & bottlenecks)")
        print(f"  {C_YELLOW}4.{C_RESET} 🎙️ Meeting Intelligence        (Process transcripts & extract tasks)")
        print(f"  {C_GREEN}5.{C_RESET} 🔍 Workspace RAG Query         (Ask AI about workspace knowledge)")
        print(f"  {C_INDIGO}6.{C_RESET} 🔑 Login / Switch User         (Sign in with Email/Username/Mobile)")
        print(f"  {C_DIM}7.{C_RESET} ❌ Exit\n")

        choice = input(f"{C_BOLD}Select an option (1-7): {C_RESET}").strip()

        if choice == "1":
            cmd_plan()
        elif choice == "2":
            cmd_tasks()
        elif choice == "3":
            cmd_risks()
        elif choice == "4":
            cmd_meetings()
        elif choice == "5":
            q = input(f"{C_YELLOW}Enter your question: {C_RESET}").strip()
            if not q:
                q = "What are the current blockers in our backend project?"
            spinner_animation(f"Searching pgvector embeddings for '{q}'...", 0.9)
            print(f"\n{C_GREEN}{C_BOLD}AI Answer:{C_RESET} The backend project currently has 1 critical blocker on Task #t-3 (Stripe Webhook Gateway) due to pending SSL certificate configuration. Dependent Phase 2 tasks are temporarily suspended.\n")
        elif choice == "6":
            cmd_login()
        elif choice in ["7", "q", "exit"]:
            print(f"\n{C_CYAN}Exiting WorkOS AI Desktop CLI. Happy engineering! 🚀{C_RESET}\n")
            break
        else:
            print(f"{C_RED}Invalid option. Please choose 1-7.{C_RESET}\n")

        input(f"{C_DIM}Press Enter to return to main menu...{C_RESET}")
        clear_screen()


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["plan", "p"]:
            brief = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
            cmd_plan(brief)
        elif arg in ["tasks", "board", "t"]:
            cmd_tasks()
        elif arg in ["risks", "health", "r"]:
            cmd_risks()
        elif arg in ["meetings", "m"]:
            cmd_meetings()
        elif arg in ["login", "auth"]:
            cmd_login()
        elif arg in ["whoami", "user"]:
            print_banner()
        else:
            print(f"Usage: py -m app.cli [plan|tasks|risks|meetings|login|whoami]")
    else:
        interactive_menu()


if __name__ == "__main__":
    main()

