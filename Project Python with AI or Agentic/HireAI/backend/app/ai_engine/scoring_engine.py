"""Scoring Engine — Deterministic 100-point compatibility scoring with transparent weights."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_WEIGHTS = {
    "mandatory_skills": 40.0,
    "preferred_skills": 15.0,
    "experience_alignment": 15.0,
    "education_alignment": 10.0,
    "projects_practical": 10.0,
    "responsibilities": 5.0,
    "soft_skills": 5.0,
}


class ScoringEngine:
    """Calculates weighted match score and produces category-wise breakdown."""

    def __init__(self, weights: dict | None = None):
        self.weights = weights or DEFAULT_WEIGHTS

    def calculate_score(
        self,
        comparisons: list[dict[str, Any]],
        candidate_info: dict[str, Any],
        job_info: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute aggregate 100-point score and category details."""
        # 1. Mandatory Skills Score (Max 40)
        mand_reqs = [c for c in comparisons if c.get("requirement_category") == "mandatory"]
        if mand_reqs:
            mand_matches = sum(
                1.0 if c["match_status"] == "matched" else (0.5 if c["match_status"] == "partially_matched" else 0.0)
                for c in mand_reqs
            )
            mand_ratio = mand_matches / len(mand_reqs)
        else:
            mand_ratio = 1.0
        mandatory_score = round(mand_ratio * self.weights["mandatory_skills"], 1)

        # 2. Preferred Skills Score (Max 15)
        pref_reqs = [c for c in comparisons if c.get("requirement_category") in ("preferred", "optional", "bonus")]
        if pref_reqs:
            pref_matches = sum(
                1.0 if c["match_status"] == "matched" else (0.5 if c["match_status"] == "partially_matched" else 0.0)
                for c in pref_reqs
            )
            pref_ratio = pref_matches / len(pref_reqs)
        else:
            pref_ratio = 0.8
        preferred_score = round(pref_ratio * self.weights["preferred_skills"], 1)

        # 3. Experience Alignment Score (Max 15)
        cand_exp = candidate_info.get("experience", [])
        job_min_exp = job_info.get("min_experience_years", 2.0) or 2.0
        exp_count = len(cand_exp)
        if exp_count >= 3:
            exp_ratio = 1.0
        elif exp_count == 2:
            exp_ratio = 0.85
        elif exp_count == 1:
            exp_ratio = 0.65
        else:
            exp_ratio = 0.40
        experience_score = round(exp_ratio * self.weights["experience_alignment"], 1)

        # 4. Education Alignment Score (Max 10)
        cand_edu = candidate_info.get("education", [])
        if cand_edu:
            education_score = round(1.0 * self.weights["education_alignment"], 1)
        else:
            education_score = round(0.5 * self.weights["education_alignment"], 1)

        # 5. Projects Practical Score (Max 10)
        cand_projects = candidate_info.get("projects", [])
        if cand_projects or exp_count >= 2:
            projects_score = round(1.0 * self.weights["projects_practical"], 1)
        elif exp_count == 1:
            projects_score = round(0.7 * self.weights["projects_practical"], 1)
        else:
            projects_score = round(0.4 * self.weights["projects_practical"], 1)

        # 6. Responsibilities Match (Max 5)
        resp_score = round(min(1.0, (mand_ratio * 0.7 + pref_ratio * 0.3)) * self.weights["responsibilities"], 1)

        # 7. Soft Skills Match (Max 5)
        soft_comparisons = [c for c in comparisons if c.get("category") == "soft_skill"]
        if soft_comparisons:
            soft_ratio = sum(1.0 for c in soft_comparisons if c["match_status"] == "matched") / len(soft_comparisons)
        else:
            soft_ratio = 0.80
        soft_skills_score = round(soft_ratio * self.weights["soft_skills"], 1)

        # Calculate Overall Score (sum of all categories, capped at 100)
        total_score = round(
            mandatory_score
            + preferred_score
            + experience_score
            + education_score
            + projects_score
            + resp_score
            + soft_skills_score,
            1,
        )
        overall_match_score = min(100.0, max(0.0, total_score))

        # Eligibility Status & Executive Summary
        if overall_match_score >= 75.0 and mandatory_score >= (self.weights["mandatory_skills"] * 0.70):
            eligibility_status = "satisfied"
            eligibility_summary = (
                f"Strong candidate match ({overall_match_score}/100). Candidate fulfills core mandatory competencies "
                f"({mandatory_score}/{self.weights['mandatory_skills']} pts) and aligns closely with target qualifications."
            )
        elif overall_match_score >= 50.0:
            eligibility_status = "partially_satisfied"
            eligibility_summary = (
                f"Moderate candidate alignment ({overall_match_score}/100). Candidate meets foundational requirements but has "
                f"addressable skill gaps in specialized qualifications."
            )
        else:
            eligibility_status = "not_satisfied"
            eligibility_summary = (
                f"Limited direct alignment ({overall_match_score}/100). Significant mandatory requirements are missing or not "
                f"evidenced in the current profile."
            )

        category_scores = {
            "mandatory_skills": mandatory_score,
            "preferred_skills": preferred_score,
            "experience_alignment": experience_score,
            "education_alignment": education_score,
            "projects_practical": projects_score,
            "responsibilities": resp_score,
            "soft_skills": soft_skills_score,
        }

        return {
            "overall_match_score": overall_match_score,
            "category_scores": category_scores,
            "eligibility_status": eligibility_status,
            "eligibility_summary": eligibility_summary,
            "weights_applied": self.weights,
        }
