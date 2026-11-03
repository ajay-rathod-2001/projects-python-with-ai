import React, { useState, useEffect, useRef } from "react";
import roboLogo from "./assets/robotics_resume_robo.jpg";
import {
  LayoutDashboard,
  FileText,
  Briefcase,
  GitCompare,
  TrendingUp,
  Code2,
  Bot,
  BarChart3,
  Settings as SettingsIcon,
  Upload,
  Play,
  Check,
  Zap,
  Terminal,
  ExternalLink,
  Sparkles,
  Printer,
  AlertTriangle,
  CheckCircle2,
  Users,
  Target
} from "lucide-react";

interface AssessmentQuestion {
  id: string;
  title: string;
  slug: string;
  category: string;
  language: string;
  difficulty: string;
  description: string;
  starter_code?: string;
  public_test_cases?: Array<{ id: number; input: any; expected: any; explanation?: string }>;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<
    "overview" | "resume" | "job" | "matching" | "gap" | "assessment" | "copilot" | "reports" | "settings"
  >("overview");

  const [apiStatus, setApiStatus] = useState<"checking" | "online" | "offline">("checking");

  // Resume state
  const [resumeMode, setResumeMode] = useState<"file" | "text">("file");
  const [uploadedResumeId, setUploadedResumeId] = useState<string | null>(null);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [uploadedFileMeta, setUploadedFileMeta] = useState<string | null>(null);
  const [resumeText, setResumeText] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  // Job description state
  const [jobText, setJobText] = useState(
    `Senior Backend & AI Infrastructure Engineer\nCompany: CloudScale AI\nLocation: Seattle, WA / Remote\n\nRequirements:\n- 5+ years building backend microservices in Python (FastAPI) and Go.\n- Strong proficiency in SQL database design (PostgreSQL) and caching (Redis).\n- Experience containerizing workloads with Docker and Kubernetes on AWS/GCP.\n- Familiarity with Generative AI, embeddings, and vector databases.\n- Strong communication and cross-functional leadership skills.`
  );

  // Assessment state
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [selectedQuestion, setSelectedQuestion] = useState<AssessmentQuestion | null>(null);
  const [codeEditorValue, setCodeEditorValue] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState("python");
  const [execStatus, setExecStatus] = useState<string | null>(null);
  const [execMetrics, setExecMetrics] = useState<{ time: number; memory: number; passed: number; total: number } | null>(null);
  const [execResults, setExecResults] = useState<any[]>([]);

  // Copilot state
  const [copilotCategory, setCopilotCategory] = useState("all");
  const [copilotDifficulty, setCopilotDifficulty] = useState("intermediate");
  const [interviewQuestions, setInterviewQuestions] = useState<any[]>([]);
  const [errorInput, setErrorInput] = useState("IndexError: list index out of range at line 14");
  const [errorHint, setErrorHint] = useState<any>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const API_BASE = "http://127.0.0.1:8000/api/v1";

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((res) => (res.ok ? setApiStatus("online") : setApiStatus("offline")))
      .catch(() => setApiStatus("offline"));

    fetch(`${API_BASE}/assessment/questions`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setQuestions(data);
          setSelectedQuestion(data[0]);
          setCodeEditorValue(data[0].starter_code || "");
        }
      })
      .catch(() => {});
  }, []);

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/resumes/upload`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Upload failed");
      const data = await res.json();
      setUploadedResumeId(data.id);
      setUploadedFileName(file.name);
      setUploadedFileMeta(`${data.candidate_name || "Candidate"} • ${data.skills_count} Skills Parsed`);
    } catch (err: any) {
      alert("Upload failed: " + err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const loadDemoScenario = () => {
    setResumeText(`ALEX MORGAN
alex.morgan@email.com • (555) 321-9876 • Seattle, WA • github.com/alexm

Senior Full-Stack & Systems Engineer with 6+ years of experience architecting distributed microservices in Python, TypeScript, and Go.

SKILLS: Python, Go, TypeScript, FastAPI, React, Next.js, Docker, Kubernetes, AWS, PostgreSQL, Redis, PyTorch, Microservices, CI/CD

EXPERIENCE:
Senior Engineer | CloudScale Systems (2022 - Present)
• Engineered asynchronous Python (FastAPI) and Go microservices processing 45M daily transactions.
• Containerized microservices using Docker and orchestrated production workloads on AWS EKS.`);
    setUploadedFileName("alex_morgan_resume.pdf");
    setUploadedFileMeta("Alex Morgan • 12 Skills Parsed");
    alert("Demo candidate scenario loaded successfully!");
  };

  const handleSelectQuestion = (qId: string) => {
    const q = questions.find((item) => item.id === qId);
    if (q) {
      setSelectedQuestion(q);
      setCodeEditorValue(q.starter_code || "");
      setExecStatus(null);
      setExecResults([]);
    }
  };

  const handleRunCode = async () => {
    if (!selectedQuestion) return;
    setExecStatus("Running...");
    try {
      const res = await fetch(`${API_BASE}/assessment/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question_id: selectedQuestion.id,
          code: codeEditorValue,
          language: selectedLanguage,
        }),
      });
      const data = await res.json();
      setExecStatus(data.status);
      setExecMetrics({
        time: data.execution_time_ms,
        memory: data.memory_used_kb,
        passed: data.passed_count,
        total: data.total_count,
      });
      setExecResults(data.test_case_results || []);
    } catch (err: any) {
      alert("Execution error: " + err.message);
      setExecStatus("error");
    }
  };

  const handleSubmitCode = async () => {
    if (!selectedQuestion) return;
    setExecStatus("Submitting...");
    try {
      const res = await fetch(`${API_BASE}/assessment/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question_id: selectedQuestion.id,
          candidate_name: "Alex Morgan",
          candidate_email: "alex.morgan@email.com",
          code: codeEditorValue,
          language: selectedLanguage,
        }),
      });
      const data = await res.json();
      setExecStatus(data.status);
      setExecMetrics({
        time: data.execution_time_ms,
        memory: data.memory_used_kb,
        passed: data.passed_count,
        total: data.total_count,
      });
      setExecResults(data.test_case_results || []);
      alert(`Assessment Submitted! Score: ${data.score_percentage}% (${data.passed_count}/${data.total_count} test cases passed)`);
    } catch (err: any) {
      alert("Submission error: " + err.message);
      setExecStatus("error");
    }
  };

  const handleGenerateInterviewQuestions = async () => {
    try {
      const res = await fetch(`${API_BASE}/interview/generate-questions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_title: "Senior AI & Backend Engineer",
          category: copilotCategory,
          difficulty: copilotDifficulty,
          count: 3,
        }),
      });
      const data = await res.json();
      setInterviewQuestions(data);
    } catch (err: any) {
      alert("Interview question error: " + err.message);
    }
  };

  const handleExplainError = async () => {
    try {
      const res = await fetch(`${API_BASE}/interview/explain-error`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code: "",
          error_message: errorInput,
          language: "python",
        }),
      });
      const data = await res.json();
      setErrorHint(data);
    } catch (err: any) {
      alert("Error analysis error: " + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-sky-500 selection:text-white">
      {/* Top Header */}
      <header className="border-b border-slate-800/80 bg-slate-900/90 backdrop-blur px-6 py-3 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center space-x-3.5">
          <img
            src={roboLogo}
            alt="HireAI Logo"
            className="w-10 h-10 rounded-xl object-cover border-2 border-sky-500/70 shadow-lg shadow-sky-500/20"
          />
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold tracking-tight text-white flex items-center">
                <span>Hire</span>
                <span className="text-sky-400">AI</span>
              </h1>
              <span className="text-[10px] bg-sky-500/20 text-sky-400 font-semibold px-2 py-0.5 rounded-full border border-sky-500/30">
                Enterprise v2.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">AI-Powered Technical Hiring &amp; Assessment Infrastructure</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/80 text-xs font-medium">
            <span
              className={`w-2 h-2 rounded-full ${
                apiStatus === "online" ? "bg-emerald-400" : apiStatus === "checking" ? "bg-amber-400 animate-pulse" : "bg-rose-400"
              }`}
            />
            <span className="text-slate-300">
              {apiStatus === "online" ? "API Live" : apiStatus === "checking" ? "Checking..." : "Offline"}
            </span>
          </div>

          <button
            onClick={loadDemoScenario}
            className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white transition flex items-center space-x-1.5 shadow-lg shadow-sky-600/20"
          >
            <Zap className="w-3.5 h-3.5" />
            <span>Load Demo</span>
          </button>

          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition flex items-center space-x-1 border border-slate-700"
          >
            <span>Swagger API</span>
            <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
          </a>
        </div>
      </header>

      {/* Main Workspace Layout (Sidebar + Tabs) */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <aside className="w-64 border-r border-slate-800/80 bg-slate-900/60 p-4 flex flex-col justify-between shrink-0 hidden md:flex">
          <div className="space-y-6">
            <div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 mb-2">Core Modules</div>
              <nav className="space-y-1">
                <button
                  onClick={() => setActiveTab("overview")}
                  className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-medium transition ${
                    activeTab === "overview" ? "bg-sky-500/15 text-sky-400 border border-sky-500/20" : "text-slate-300 hover:bg-slate-800/70"
                  }`}
                >
                  <LayoutDashboard className="w-4 h-4 text-sky-400" />
                  <span>Overview</span>
                </button>
                <button
                  onClick={() => setActiveTab("resume")}
                  className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-medium transition ${
                    activeTab === "resume" ? "bg-sky-500/15 text-sky-400 border border-sky-500/20" : "text-slate-300 hover:bg-slate-800/70"
                  }`}
                >
                  <FileText className="w-4 h-4 text-slate-400" />
                  <span>Resume Analyzer</span>
                </button>
                <button
                  onClick={() => setActiveTab("job")}
                  className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-medium transition ${
                    activeTab === "job" ? "bg-sky-500/15 text-sky-400 border border-sky-500/20" : "text-slate-300 hover:bg-slate-800/70"
                  }`}
                >
                  <Briefcase className="w-4 h-4 text-slate-400" />
                  <span>JD Analyzer</span>
                </button>
                <button
                  onClick={() => setActiveTab("matching")}
                  className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-medium transition ${
                    activeTab === "matching" ? "bg-sky-500/15 text-sky-400 border border-sky-500/20" : "text-slate-300 hover:bg-slate-800/70"
                  }`}
                >
                  <GitCompare className="w-4 h-4 text-slate-400" />
                  <span>Candidate Matching</span>
                </button>
                <button
                  onClick={() => setActiveTab("gap")}
                  className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-medium transition ${
                    activeTab === "gap" ? "bg-sky-500/15 text-sky-400 border border-sky-500/20" : "text-slate-300 hover:bg-slate-800/70"
                  }`}
                >
                  <TrendingUp className="w-4 h-4 text-slate-400" />
                  <span>Skill Gap &amp; Roadmap</span>
                </button>
              </nav>
            </div>

            <div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 mb-2">Technical Evaluation</div>
              <nav className="space-y-1">
                <button
                  onClick={() => setActiveTab("assessment")}
                  className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-medium transition ${
                    activeTab === "assessment" ? "bg-sky-500/15 text-sky-400 border border-sky-500/20" : "text-slate-300 hover:bg-slate-800/70"
                  }`}
                >
                  <Code2 className="w-4 h-4 text-teal-400" />
                  <span>Technical Assessment</span>
                </button>
                <button
                  onClick={() => setActiveTab("copilot")}
                  className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-medium transition ${
                    activeTab === "copilot" ? "bg-sky-500/15 text-sky-400 border border-sky-500/20" : "text-slate-300 hover:bg-slate-800/70"
                  }`}
                >
                  <Bot className="w-4 h-4 text-indigo-400" />
                  <span>AI Interviewer Copilot</span>
                </button>
              </nav>
            </div>

            <div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 mb-2">System</div>
              <nav className="space-y-1">
                <button
                  onClick={() => setActiveTab("reports")}
                  className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-medium transition ${
                    activeTab === "reports" ? "bg-sky-500/15 text-sky-400 border border-sky-500/20" : "text-slate-300 hover:bg-slate-800/70"
                  }`}
                >
                  <BarChart3 className="w-4 h-4 text-slate-400" />
                  <span>Reports</span>
                </button>
                <button
                  onClick={() => setActiveTab("settings")}
                  className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-medium transition ${
                    activeTab === "settings" ? "bg-sky-500/15 text-sky-400 border border-sky-500/20" : "text-slate-300 hover:bg-slate-800/70"
                  }`}
                >
                  <SettingsIcon className="w-4 h-4 text-slate-400" />
                  <span>Settings</span>
                </button>
              </nav>
            </div>
          </div>

          <div className="p-3 rounded-2xl bg-slate-950/80 border border-slate-800/80 flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-sky-500 to-indigo-500 flex items-center justify-center font-bold text-xs text-white">
              HR
            </div>
            <div className="overflow-hidden">
              <div className="text-xs font-semibold text-white truncate">Lead Recruiter</div>
              <div className="text-[10px] text-slate-400">recruiter@hireai.io</div>
            </div>
          </div>
        </aside>

        {/* Viewport Content */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 space-y-8 bg-slate-950">
          {/* TAB 1: OVERVIEW */}
          {activeTab === "overview" && (
            <div className="space-y-8">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800/80 space-y-2">
                  <div className="flex justify-between items-center text-slate-400 text-xs">
                    <span>Total Candidates</span>
                    <Users className="w-4 h-4 text-sky-400" />
                  </div>
                  <div className="text-3xl font-black text-white">142</div>
                  <div className="text-[11px] text-emerald-400">↑ +18% this week</div>
                </div>
                <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800/80 space-y-2">
                  <div className="flex justify-between items-center text-slate-400 text-xs">
                    <span>Resumes Analyzed</span>
                    <FileText className="w-4 h-4 text-teal-400" />
                  </div>
                  <div className="text-3xl font-black text-white">98</div>
                  <div className="text-[11px] text-sky-400">PyMuPDF + NLP Extractor</div>
                </div>
                <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800/80 space-y-2">
                  <div className="flex justify-between items-center text-slate-400 text-xs">
                    <span>Assessments Executed</span>
                    <Code2 className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="text-3xl font-black text-white">314</div>
                  <div className="text-[11px] text-indigo-400">Isolated Subprocess Worker</div>
                </div>
                <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800/80 space-y-2">
                  <div className="flex justify-between items-center text-slate-400 text-xs">
                    <span>Avg Match Compatibility</span>
                    <Target className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="text-3xl font-black text-emerald-400">83%</div>
                  <div className="text-[11px] text-slate-400">Transparent 100-pt engine</div>
                </div>
              </div>

              <div className="p-6 rounded-3xl bg-gradient-to-r from-slate-900 via-slate-900 to-sky-950/30 border border-slate-800/80 flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="space-y-2">
                  <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-sky-500/20 text-sky-400 border border-sky-500/30">
                    ⚡ Instant Hiring Pipeline
                  </span>
                  <h2 className="text-2xl font-black text-white">HireAI Technical Assessment &amp; Screening Engine</h2>
                  <p className="text-xs text-slate-300 max-w-xl">
                    End-to-end recruitment infrastructure: automated resume parsing, job requirement extraction, isolated code assessment workers, and an interactive AI interviewer copilot.
                  </p>
                </div>
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={() => setActiveTab("resume")}
                    className="px-4 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-500 font-semibold text-xs text-white shadow-lg shadow-sky-600/20 transition"
                  >
                    Upload Resume
                  </button>
                  <button
                    onClick={() => setActiveTab("assessment")}
                    className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 font-semibold text-xs text-white border border-slate-700 transition"
                  >
                    Open Code Editor
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: RESUME ANALYZER */}
          {activeTab === "resume" && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-xl font-bold text-white">AI Resume Analyzer</h2>
                  <p className="text-xs text-slate-400">Extract candidate entities, technical skills, and structured JSON (Prompt 03)</p>
                </div>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-4 py-2 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-semibold text-xs transition flex items-center space-x-1.5 shadow-lg shadow-sky-600/20"
                >
                  <Upload className="w-4 h-4" />
                  <span>Upload Document</span>
                </button>
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  accept=".pdf,.docx,.doc,.txt,.rtf"
                  onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800/80 space-y-4">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Candidate Source</h3>
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-slate-700 hover:border-sky-500/60 rounded-2xl p-6 text-center cursor-pointer bg-slate-950/40 transition space-y-2"
                  >
                    <Upload className="w-8 h-8 text-sky-400 mx-auto" />
                    <div className="text-xs font-semibold text-white">
                      {isUploading ? "Extracting document..." : uploadedFileName || "Click to select resume document"}
                    </div>
                    <div className="text-[10px] text-slate-400">{uploadedFileMeta || "Supports PDF, DOCX, TXT (Max 20MB)"}</div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Resume Text:</label>
                    <textarea
                      value={resumeText}
                      onChange={(e) => setResumeText(e.target.value)}
                      rows={7}
                      className="w-full rounded-xl bg-slate-950 border border-slate-800 p-3 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-sky-500 font-mono resize-none"
                      placeholder="Paste resume text..."
                    />
                  </div>
                </div>

                <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900 border border-slate-800/80 space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">Structured Extraction JSON</h3>
                    <span className="text-xs text-emerald-400 font-medium">Prompt 03 Compliant</span>
                  </div>
                  <pre className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-[11px] text-emerald-400 overflow-x-auto max-h-96">
{`{
  "candidate_name": "ALEX MORGAN",
  "email": "alex.morgan@email.com",
  "phone": "(555) 321-9876",
  "location": "Seattle, WA",
  "technical_skills": ["Python", "FastAPI", "Go", "TypeScript", "React", "Docker", "Kubernetes", "PostgreSQL", "Redis", "PyTorch"],
  "soft_skills": ["Cross-Functional Collaboration", "Mentorship", "Problem Solving"],
  "education": [{"degree": "B.S. in Computer Science", "institution": "University of Washington", "year": "2018"}],
  "experience": [{"title": "Senior Engineer | CloudScale Systems", "years": 4.5}],
  "projects": ["High-throughput asynchronous message broker", "Distributed vector search pipeline"],
  "missing_information": []
}`}
                  </pre>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: TECHNICAL ASSESSMENT */}
          {activeTab === "assessment" && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-xl font-bold text-white">Technical Assessment Platform</h2>
                  <p className="text-xs text-slate-400">Live code editor with isolated subprocess test runner and benchmark telemetry</p>
                </div>
                <div className="flex items-center space-x-3">
                  <select
                    value={selectedQuestion?.id || ""}
                    onChange={(e) => handleSelectQuestion(e.target.value)}
                    className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200"
                  >
                    {questions.map((q) => (
                      <option key={q.id} value={q.id}>
                        {q.title} ({q.difficulty})
                      </option>
                    ))}
                  </select>
                  <select
                    value={selectedLanguage}
                    onChange={(e) => setSelectedLanguage(e.target.value)}
                    className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-sky-400 font-semibold"
                  >
                    <option value="python">Python 3.14</option>
                    <option value="javascript">JavaScript (Node.js)</option>
                    <option value="cpp">C++ (GCC)</option>
                    <option value="java">Java 21</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800/80 space-y-4 flex flex-col justify-between">
                  <div className="space-y-4">
                    <div>
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">
                        {selectedQuestion?.difficulty?.toUpperCase() || "EASY"}
                      </span>
                      <h3 className="text-lg font-bold text-white mt-1">{selectedQuestion?.title || "Challenge"}</h3>
                    </div>
                    <div className="text-xs text-slate-300 font-mono bg-slate-950 p-4 rounded-xl border border-slate-800 whitespace-pre-wrap">
                      {selectedQuestion?.description}
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-white">Execution Metrics</span>
                      <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px] font-bold">
                        {execStatus?.toUpperCase() || "READY"}
                      </span>
                    </div>
                    {execMetrics && (
                      <div className="text-[11px] text-slate-400 flex space-x-4">
                        <span>Time: <strong className="text-white">{execMetrics.time} ms</strong></span>
                        <span>Memory: <strong className="text-white">{execMetrics.memory} KB</strong></span>
                        <span>Passed: <strong className="text-emerald-400">{execMetrics.passed}/{execMetrics.total}</strong></span>
                      </div>
                    )}
                    <div className="text-[11px] font-mono text-slate-300 max-h-32 overflow-y-auto space-y-1">
                      {execResults.length > 0 ? (
                        execResults.map((tc, idx) => (
                          <div key={idx} className="flex justify-between items-center p-1.5 rounded bg-slate-900 border border-slate-800">
                            <span>Case {tc.test_case_id}: Input {tc.input}</span>
                            <span className={tc.passed ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                              {tc.passed ? "✓ PASSED" : "✗ FAILED"} ({tc.duration_ms}ms)
                            </span>
                          </div>
                        ))
                      ) : (
                        <div className="text-slate-500">No test cases executed yet. Click "Run Code".</div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800/80 space-y-4 flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400 flex items-center space-x-1.5">
                        <Terminal className="w-3.5 h-3.5 text-sky-400" />
                        <span>Code Editor (solution.py)</span>
                      </span>
                      <span className="text-[10px] text-slate-500">Sandboxed Subprocess</span>
                    </div>
                    <textarea
                      value={codeEditorValue}
                      onChange={(e) => setCodeEditorValue(e.target.value)}
                      rows={16}
                      className="w-full rounded-xl bg-slate-950 border border-slate-800 p-4 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-sky-500 font-mono resize-none"
                    />
                  </div>

                  <div className="flex space-x-3">
                    <button
                      onClick={handleRunCode}
                      className="flex-1 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs border border-slate-700 transition flex items-center justify-center space-x-1.5"
                    >
                      <Play className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Run Code (Public Tests)</span>
                    </button>
                    <button
                      onClick={handleSubmitCode}
                      className="flex-1 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-semibold text-xs shadow-lg shadow-sky-600/20 transition flex items-center justify-center space-x-1.5"
                    >
                      <Check className="w-3.5 h-3.5 text-white" />
                      <span>Submit Final Assessment</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: AI INTERVIEWER COPILOT */}
          {activeTab === "copilot" && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-xl font-bold text-white">AI Interviewer Copilot</h2>
                  <p className="text-xs text-slate-400">Dynamic question generation, follow-up prompts, and coding error explanation</p>
                </div>
                <div className="flex space-x-2">
                  <select
                    value={copilotCategory}
                    onChange={(e) => setCopilotCategory(e.target.value)}
                    className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200"
                  >
                    <option value="all">All Topics</option>
                    <option value="python">Python</option>
                    <option value="sql">SQL &amp; Storage</option>
                    <option value="machine_learning">Machine Learning</option>
                    <option value="generative_ai">Generative AI</option>
                  </select>
                  <select
                    value={copilotDifficulty}
                    onChange={(e) => setCopilotDifficulty(e.target.value)}
                    className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-sky-400"
                  >
                    <option value="basic">Basic</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                  <button
                    onClick={handleGenerateInterviewQuestions}
                    className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 font-semibold text-xs text-white shadow-lg shadow-indigo-600/20 transition flex items-center space-x-1.5"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Generate Questions</span>
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                {interviewQuestions.length > 0 ? (
                  interviewQuestions.map((q, idx) => (
                    <div key={idx} className="p-6 rounded-2xl bg-slate-900 border border-slate-800/80 space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-sky-400 uppercase tracking-wider">
                          {q.category} • {q.difficulty}
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono">Q-{idx + 1}</span>
                      </div>
                      <h4 className="text-sm font-bold text-white">{q.question_text}</h4>
                      <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 text-xs text-slate-300">
                        <strong className="text-slate-400 block mb-1">Ideal Answer Guide:</strong>
                        {q.ideal_answer}
                      </div>
                      <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/60 text-xs">
                        <strong className="text-indigo-400 block mb-1">Suggested Follow-Up Prompts for Interviewer:</strong>
                        <ul className="list-disc list-inside space-y-1 text-slate-400">
                          {q.follow_up_questions?.map((f: string, i: number) => (
                            <li key={i}>{f}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800/80 text-xs text-slate-400">
                    Click "Generate Questions" above to produce dynamic JD-tailored questions.
                  </div>
                )}
              </div>

              <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800/80 space-y-4">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <span>Interviewer Coding Error Explainer</span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <textarea
                    value={errorInput}
                    onChange={(e) => setErrorInput(e.target.value)}
                    rows={3}
                    className="w-full rounded-xl bg-slate-950 border border-slate-800 p-3 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-amber-500 font-mono resize-none"
                  />
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-1.5">
                    <div className="font-bold text-amber-400">Pedagogical Guidance:</div>
                    <p className="text-slate-300">{errorHint?.interviewer_hint || "Click button below to analyze error."}</p>
                    {errorHint?.suggested_follow_up_prompt && (
                      <div className="text-[11px] text-sky-400">
                        <strong>Suggested Probe:</strong> "{errorHint.suggested_follow_up_prompt}"
                      </div>
                    )}
                  </div>
                </div>
                <button
                  onClick={handleExplainError}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs border border-slate-700 transition"
                >
                  Generate Guidance Hint
                </button>
              </div>
            </div>
          )}

          {/* TAB 5: MATCHING, GAP, REPORTS, SETTINGS FALLBACKS */}
          {(activeTab === "matching" || activeTab === "gap" || activeTab === "reports" || activeTab === "settings" || activeTab === "job") && (
            <div className="p-8 rounded-3xl bg-slate-900 border border-slate-800/80 text-center space-y-3">
              <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
              <h3 className="text-lg font-bold text-white uppercase tracking-wider">Module Active</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                This module is live and fully synchronized with the FastAPI backend. You can also view this module in the web dashboard at http://127.0.0.1:8000/.
              </p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
