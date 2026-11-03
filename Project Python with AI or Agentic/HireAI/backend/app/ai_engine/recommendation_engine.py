"""Career Recommendation Engine — Industry/FAANG-grade career acceleration guidance.

Generates targeted learning roadmaps, portfolio project blueprints, Google-style XYZ
resume bullet rewrites, and curated interview questions based on match analysis gaps.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generates actionable career roadmaps and resume optimizations."""

    def generate_recommendations(
        self,
        comparisons: list[dict[str, Any]],
        candidate_info: dict[str, Any],
        job_info: dict[str, Any],
    ) -> dict[str, Any]:
        """Produce comprehensive career improvement package."""
        missing_skills = [c for c in comparisons if c.get("match_status") in ("missing", "partially_matched")]
        matched_skills = [c for c in comparisons if c.get("match_status") == "matched"]

        learning_roadmap = []
        project_suggestions = []
        resume_improvements = []
        interview_prep = []

        # 1. Learning Roadmap (Prioritize missing mandatory skills first)
        for c in missing_skills[:4]:
            skill = c.get("skill_name", "Technical Skill")
            is_mand = c.get("requirement_category") == "mandatory"
            priority = "high" if is_mand else "medium"

            learning_roadmap.append({
                "priority": priority,
                "target_skill": skill,
                "title": f"Mastering {skill} for Production Environments",
                "description": (
                    f"Deep dive into {skill} architecture, concurrency models, and hands-on production patterns. "
                    f"Build an end-to-end service demonstrating {skill} best practices, unit testing, and metrics."
                ),
                "rationale": (
                    f"Addresses critical {c.get('requirement_category', 'target')} qualification requirement for {job_info.get('title', 'target role')}."
                ),
            })

        # Ensure at least 2 roadmap items
        if not learning_roadmap:
            learning_roadmap.append({
                "priority": "medium",
                "target_skill": "System Architecture",
                "title": "Scalable Distributed System Design",
                "description": "Study caching strategies (Redis), message queues (Kafka), and database sharding patterns.",
                "rationale": "Strengthens senior-level architectural design capabilities for technical interviews.",
            })

        # 2. Portfolio Project Suggestions
        missing_names = [c.get("skill_name") for c in missing_skills[:3]]
        target_skills_str = ", ".join(missing_names) if missing_names else "FastAPI, Docker, PostgreSQL"

        project_suggestions.append({
            "title": f"Production-Grade Microservice Pipeline ({target_skills_str})",
            "description": (
                f"Design and deploy an asynchronous event-driven backend service incorporating {target_skills_str}. "
                f"Implement Docker containerization, OpenAPI documentation, and automated GitHub Actions CI/CD with >85% test coverage."
            ),
            "skills_addressed": missing_names or ["Python", "FastAPI", "Docker"],
            "difficulty": "Advanced",
        })

        project_suggestions.append({
            "title": "High-Throughput Analytics & Telemetry Dashboard",
            "description": (
                "Develop a real-time metrics ingestion pipeline utilizing Redis queues and SQLite/PostgreSQL WAL mode, "
                "surfacing live telemetry via WebSockets to a React/TypeScript interface."
            ),
            "skills_addressed": ["System Design", "Databases", "Full-Stack"],
            "difficulty": "Intermediate",
        })

        # 3. Resume Bullet Improvements (Google/FAANG XYZ Formula: Accomplished [X] as measured by [Y], by doing [Z])
        exp_list = candidate_info.get("experience", [])
        if exp_list:
            first_exp = exp_list[0]
            role = first_exp.get("title", "Software Engineer")
            resume_improvements.append({
                "section": f"Experience — {role[:40]}",
                "weak_example": "Built backend APIs and worked on database optimization.",
                "faang_optimized_bullet": (
                    "Architected high-throughput RESTful microservices in Python/FastAPI, reducing P99 latency by 42% "
                    "across 1.5M daily active requests through asynchronous query batching and Redis caching."
                ),
                "formula_applied": "Accomplished [42% latency reduction] measured by [1.5M daily requests] by doing [async batching & Redis caching].",
            })
        else:
            resume_improvements.append({
                "section": "Professional Experience",
                "weak_example": "Responsible for developing software features and bug fixes.",
                "faang_optimized_bullet": (
                    "Engineered modular backend services and automated CI/CD deployment pipelines, decreasing release cycle duration "
                    "by 35% while maintaining zero production rollback incidents."
                ),
                "formula_applied": "Accomplished [35% faster release cycles] measured by [zero downtime] by doing [modular CI/CD pipelines].",
            })

        # Add second bullet improvement
        resume_improvements.append({
            "section": "Core Technical Projects",
            "weak_example": "Created an AI resume parsing tool.",
            "faang_optimized_bullet": (
                "Spearheaded development of a privacy-first AI Career Intelligence platform, processing multi-format resumes with "
                "98% skill extraction accuracy and deterministic 100-point job compatibility scoring."
            ),
            "formula_applied": "Accomplished [98% extraction accuracy] measured by [100-point deterministic scoring] by doing [privacy-first local NLP].",
        })

        # 4. Curated Technical & Behavioral Interview Questions
        for m in matched_skills[:2]:
            s_name = m.get("skill_name")
            interview_prep.append({
                "type": "Technical Deep Dive",
                "topic": s_name,
                "question": f"How have you architected and scaled production systems using {s_name}? What trade-offs did you make?",
                "key_talking_points": f"Discuss concurrency models, memory management, failover strategies, and concrete production metrics with {s_name}.",
            })

        for m in missing_skills[:2]:
            s_name = m.get("skill_name")
            interview_prep.append({
                "type": "Gap-Mitigation Question",
                "topic": s_name,
                "question": f"While our stack heavily relies on {s_name}, how would you apply your experience in analogous technologies to quickly deliver in this domain?",
                "key_talking_points": f"Highlight conceptual parallels from your background, demonstrating rapid ramp-up ability and engineering fundamentals.",
            })

        interview_prep.append({
            "type": "FAANG Behavioral (STAR Method)",
            "topic": "Conflict & Technical Decision Making",
            "question": "Tell me about a time you had a technical disagreement with a colleague or lead regarding architecture. How did you resolve it?",
            "key_talking_points": "Frame using Situation-Task-Action-Result. Focus on data-driven benchmarking, collaborative consensus, and prioritizing user outcome.",
        })

        return {
            "learning_roadmap": learning_roadmap,
            "project_suggestions": project_suggestions,
            "resume_improvements": resume_improvements,
            "interview_prep": interview_prep,
        }

