"""Matching Engine — Compares candidate skills against job requirements."""

import logging
from typing import Any
from app.ai_engine.embedding_engine import EmbeddingEngine

logger = logging.getLogger(__name__)


class MatchingEngine:
    """Executes semantic comparison between candidate resume evidence and job requirements."""

    def __init__(self):
        self.embedding_engine = EmbeddingEngine()

    def compare_skills(
        self,
        resume_skills: list[dict[str, Any]],
        job_requirements: list[dict[str, Any]],
        resume_raw_text: str = "",
    ) -> list[dict[str, Any]]:
        """Classify each requirement as matched, partially_matched, missing, or not_verifiable.

        Returns:
            List of comparison objects with status, score, resume evidence, and explanation.
        """
        comparisons = []
        resume_skill_names = {s.get("skill_name", "").lower(): s for s in resume_skills}
        resume_text_lower = resume_raw_text.lower() if resume_raw_text else ""

        for req in job_requirements:
            req_name = req.get("requirement_name", "")
            req_name_lower = req_name.lower()
            req_classification = req.get("classification", "mandatory")
            req_category = req.get("category", "technical")
            req_evidence = req.get("evidence_text", "")

            # 1. Direct or alias match check
            best_score = 0.0
            best_evidence = ""
            match_status = "missing"
            explanation = ""

            if req_name_lower in resume_skill_names:
                best_score = 1.0
                cand_skill = resume_skill_names[req_name_lower]
                best_evidence = cand_skill.get("evidence_text") or f"Direct proficiency demonstrated in {req_name}."
                match_status = "matched"
                explanation = f"Exact skill match: Candidate explicitly demonstrates proficiency in {req_name}."

            elif req_name_lower in resume_text_lower:
                # Found in raw text directly
                best_score = 0.90
                # Extract snippet from resume
                idx = resume_text_lower.find(req_name_lower)
                start = max(0, idx - 80)
                end = min(len(resume_raw_text), idx + len(req_name) + 120)
                best_evidence = resume_raw_text[start:end].strip()
                match_status = "matched"
                explanation = f"Contextual match: Mentioned directly in candidate work history/projects."

            else:
                # 2. Semantic comparison against all candidate skills
                highest_sim = 0.0
                closest_skill = None

                for s_name, s_obj in resume_skill_names.items():
                    sim = self.embedding_engine.compute_similarity(req_name, s_name)
                    if sim > highest_sim:
                        highest_sim = sim
                        closest_skill = s_obj

                best_score = round(highest_sim, 2)

                if highest_sim >= 0.75:
                    match_status = "matched"
                    best_evidence = closest_skill.get("evidence_text") if closest_skill else ""
                    closest_name = closest_skill.get("skill_name") if closest_skill else ""
                    explanation = f"High semantic alignment between requested '{req_name}' and candidate's '{closest_name}'."
                elif highest_sim >= 0.45:
                    match_status = "partially_matched"
                    best_evidence = closest_skill.get("evidence_text") if closest_skill else ""
                    closest_name = closest_skill.get("skill_name") if closest_skill else ""
                    explanation = f"Adjacent competency: Candidate demonstrates background in '{closest_name}', which transfers to '{req_name}'."
                else:
                    match_status = "missing"
                    best_evidence = "No evidence found in uploaded resume document."
                    explanation = f"Requirement '{req_name}' ({req_classification}) is not evidenced in the candidate profile."

            comparisons.append({
                "requirement_id": req.get("id"),
                "skill_name": req_name,
                "requirement_category": req_classification,
                "category": req_category,
                "match_status": match_status,
                "semantic_score": best_score,
                "resume_evidence": best_evidence,
                "explanation": explanation,
            })

        return comparisons
