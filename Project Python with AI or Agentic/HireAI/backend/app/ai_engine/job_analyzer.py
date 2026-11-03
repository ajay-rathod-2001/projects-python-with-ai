"""Job Analyzer — Parses job descriptions into classified requirements."""

import logging
import re
from typing import Any
from app.ai_engine.skill_extractor import SKILL_TAXONOMY, SkillExtractor

logger = logging.getLogger(__name__)


class JobAnalyzer:
    """Analyzes job postings to extract mandatory, preferred, and bonus qualifications."""

    def __init__(self):
        self.skill_extractor = SkillExtractor()

    def analyze_job(self, text: str) -> dict[str, Any]:
        """Extract title, company, requirements, experience levels, and classifications from job text."""
        if not text:
            return {
                "title": "Software Engineering Position",
                "company": "Target Company",
                "location": "Remote",
                "min_experience_years": 3.0,
                "education_level": "Bachelor's Degree",
                "requirements": [],
            }

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # 1. Infer Title and Company
        title = "Software Engineer"
        company = "Target Organization"
        location = "Remote / Hybrid"

        title_patterns = [
            r"(Senior\s+|Staff\s+|Principal\s+|Lead\s+)?(Software|Backend|Frontend|Full[\s-]Stack|DevOps|Cloud|Data|Machine\s+Learning|AI)\s+(Engineer|Developer|Architect)",
            r"Product\s+Manager|Data\s+Scientist|Engineering\s+Manager",
        ]
        for line in lines[:8]:
            for p in title_patterns:
                match = re.search(p, line, re.IGNORECASE)
                if match:
                    title = match.group(0).strip()
                    break
            if title != "Software Engineer":
                break

        # Check for company mentions: "at Company" or "about Company"
        comp_match = re.search(r"(?:at|join|about)\s+([A-Z][a-zA-Z0-9&.\s]{2,30})", text[:500])
        if comp_match:
            cand = comp_match.group(1).strip()
            if cand.lower() not in ["the", "our", "a", "an", "we"]:
                company = cand

        # 2. Extract Minimum Experience Years
        min_experience_years = 2.0
        exp_match = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:-\s*\d+\s*)?(?:years?|yrs?)\s+of\s+(?:experience|relevant)", text, re.IGNORECASE)
        if exp_match:
            try:
                min_experience_years = float(exp_match.group(1))
            except ValueError:
                min_experience_years = 3.0

        # 3. Extract Education Level
        education_level = "Bachelor's in Computer Science or equivalent"
        if re.search(r"\bph\.?d\b", text, re.IGNORECASE):
            education_level = "Ph.D. in Computer Science or related field"
        elif re.search(r"\b(?:master|ms|m\.s\.)\b", text, re.IGNORECASE):
            education_level = "Master's Degree in Computer Science or related field"
        elif re.search(r"\b(?:bachelor|bs|b\.s\.|b\.tech)\b", text, re.IGNORECASE):
            education_level = "Bachelor's Degree in Computer Science or related STEM field"

        # 4. Classify Skills and Requirements
        extracted_skills = self.skill_extractor.extract_skills(text)
        requirements = []

        # Find section markers in text to determine mandatory vs preferred
        lower_text = text.lower()
        pref_markers = ["preferred", "nice to have", "plus", "bonus", "desirable", "good to have", "optional"]
        mand_markers = ["required", "minimum", "must have", "qualifications", "basic qualifications", "essential", "core"]

        for skill in extracted_skills:
            name = skill["skill_name"]
            category = skill["category"]
            evidence = skill["evidence_text"]

            # Context classification
            surrounding_window = self._get_context_window(text, name)
            classification = "mandatory"

            if any(m in surrounding_window for m in pref_markers):
                classification = "preferred"
            elif any(m in surrounding_window for m in mand_markers):
                classification = "mandatory"
            else:
                # Default technical languages/frameworks to mandatory, cloud/devops/soft skills to preferred if not specified
                classification = "mandatory" if category in ("language", "framework") else "preferred"

            requirements.append({
                "requirement_name": name,
                "category": category,
                "classification": classification,
                "required_experience_years": min_experience_years if classification == "mandatory" else None,
                "evidence_text": evidence,
                "is_ambiguous": False,
            })

        # Ensure we have at least standard requirements if none detected
        if not requirements:
            requirements = [
                {
                    "requirement_name": "Python",
                    "category": "language",
                    "classification": "mandatory",
                    "required_experience_years": min_experience_years,
                    "evidence_text": "Strong programming experience in modern languages.",
                    "is_ambiguous": False,
                },
                {
                    "requirement_name": "FastAPI",
                    "category": "framework",
                    "classification": "mandatory",
                    "required_experience_years": min_experience_years,
                    "evidence_text": "Experience building backend microservices and REST APIs.",
                    "is_ambiguous": False,
                },
                {
                    "requirement_name": "Docker",
                    "category": "devops",
                    "classification": "preferred",
                    "required_experience_years": None,
                    "evidence_text": "Containerization and cloud deployment experience.",
                    "is_ambiguous": False,
                },
            ]

        return {
            "title": title,
            "company": company,
            "location": location,
            "min_experience_years": min_experience_years,
            "education_level": education_level,
            "requirements": requirements,
        }

    def _get_context_window(self, text: str, word: str, window_chars: int = 150) -> str:
        """Find the text around a word occurrence to detect classification cues."""
        idx = text.lower().find(word.lower())
        if idx == -1:
            return ""
        start = max(0, idx - window_chars)
        end = min(len(text), idx + len(word) + window_chars)
        return text[start:end].lower()
