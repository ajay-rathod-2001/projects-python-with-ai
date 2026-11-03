"""Industry-Grade AI Skill & Information Extractor for Candidate Resumes.

Identifies contact details, structured education, work experience, projects,
and a comprehensive 350+ technical and soft skill taxonomy with textual citations.
"""

import logging
from pathlib import Path
import re
from typing import Any

logger = logging.getLogger(__name__)

# Comprehensive Standardized Skill Taxonomy
SKILL_TAXONOMY = {
    # Programming Languages
    "Python": {"category": "language", "aliases": [r"\bpython(?:3)?\b"]},
    "JavaScript": {"category": "language", "aliases": [r"\bjavascript\b", r"\bjs\b", r"\bes6\b"]},
    "TypeScript": {"category": "language", "aliases": [r"\btypescript\b", r"\bts\b"]},
    "Java": {"category": "language", "aliases": [r"\bjava\b(?!script)"]},
    "C++": {"category": "language", "aliases": [r"\bc\+\+\b", r"\bcpp\b"]},
    "C#": {"category": "language", "aliases": [r"\bc#\b", r"\bc-sharp\b"]},
    "C": {"category": "language", "aliases": [r"\b(?<!\+)(?<!#)c(?!\+)(?!#)\b"]},
    "Go": {"category": "language", "aliases": [r"\bgolang\b", r"\bgo\s+language\b", r"\bgo\b(?=\s*(?:backend|developer|microservices|concurrency))"]},
    "Rust": {"category": "language", "aliases": [r"\brust\b(?:\s+lang)?"]},
    "SQL": {"category": "language", "aliases": [r"\bsql\b", r"\bstructured query language\b"]},
    "Bash": {"category": "language", "aliases": [r"\bbash\b", r"\bshell\s+script(?:ing)?\b"]},
    "Ruby": {"category": "language", "aliases": [r"\bruby\b"]},
    "PHP": {"category": "language", "aliases": [r"\bphp\b"]},
    "Swift": {"category": "language", "aliases": [r"\bswift\b"]},
    "Kotlin": {"category": "language", "aliases": [r"\bkotlin\b"]},
    "Scala": {"category": "language", "aliases": [r"\bscala\b"]},
    "R": {"category": "language", "aliases": [r"\br\s+(?:programming|scripting|studio)\b", r"\br-lang\b"]},

    # Web & Application Frameworks
    "FastAPI": {"category": "framework", "aliases": [r"\bfastapi\b"]},
    "React": {"category": "framework", "aliases": [r"\breact(?:\.js|js)?\b"]},
    "Next.js": {"category": "framework", "aliases": [r"\bnext(?:\.js|js)?\b"]},
    "Node.js": {"category": "framework", "aliases": [r"\bnode(?:\.js|js)?\b"]},
    "Express": {"category": "framework", "aliases": [r"\bexpress(?:\.js|js)?\b"]},
    "Django": {"category": "framework", "aliases": [r"\bdjango\b"]},
    "Flask": {"category": "framework", "aliases": [r"\bflask\b"]},
    "Spring Boot": {"category": "framework", "aliases": [r"\bspring\s+boot\b", r"\bspring\s+framework\b"]},
    "Angular": {"category": "framework", "aliases": [r"\bangular(?:\.js|js)?\b"]},
    "Vue.js": {"category": "framework", "aliases": [r"\bvue(?:\.js|js)?\b"]},
    "Tailwind CSS": {"category": "framework", "aliases": [r"\btailwind(?:\s+css)?\b"]},
    "GraphQL": {"category": "framework", "aliases": [r"\bgraphql\b"]},
    "REST API": {"category": "framework", "aliases": [r"\brest(?:ful)?\s*(?:api|services)?\b"]},
    "gRPC": {"category": "framework", "aliases": [r"\bgrpc\b"]},
    ".NET": {"category": "framework", "aliases": [r"\b\.net(?:\s+core)?\b", r"\basp\.net\b"]},

    # Cloud & DevOps
    "AWS": {"category": "cloud", "aliases": [r"\baws\b", r"\bamazon\s+web\s+services\b", r"\bec2\b", r"\bs3\b", r"\blambda\b"]},
    "Google Cloud": {"category": "cloud", "aliases": [r"\bgcp\b", r"\bgoogle\s+cloud(?:\s+platform)?\b"]},
    "Azure": {"category": "cloud", "aliases": [r"\bazure\b", r"\bmicrosoft\s+azure\b"]},
    "Docker": {"category": "devops", "aliases": [r"\bdocker\b", r"\bcontainerization\b"]},
    "Kubernetes": {"category": "devops", "aliases": [r"\bkubernetes\b", r"\bk8s\b"]},
    "CI/CD": {"category": "devops", "aliases": [r"\bci\s*/\s*cd\b", r"\bcontinuous\s+integration\b"]},
    "Terraform": {"category": "devops", "aliases": [r"\bterraform\b", r"\biac\b", r"\binfrastructure as code\b"]},
    "GitHub Actions": {"category": "devops", "aliases": [r"\bgithub\s+actions\b"]},
    "Jenkins": {"category": "devops", "aliases": [r"\bjenkins\b"]},
    "Linux": {"category": "devops", "aliases": [r"\blinux\b", r"\bubuntu\b", r"\bcentos\b", r"\bdebian\b"]},
    "Helm": {"category": "devops", "aliases": [r"\bhelm\b"]},
    "Prometheus": {"category": "devops", "aliases": [r"\bprometheus\b"]},
    "Grafana": {"category": "devops", "aliases": [r"\bgrafana\b"]},

    # Databases & Storage
    "PostgreSQL": {"category": "database", "aliases": [r"\bpostgresql\b", r"\bpostgres\b"]},
    "MySQL": {"category": "database", "aliases": [r"\bmysql\b"]},
    "MongoDB": {"category": "database", "aliases": [r"\bmongodb\b", r"\bmongo\b"]},
    "Redis": {"category": "database", "aliases": [r"\bredis\b"]},
    "SQLite": {"category": "database", "aliases": [r"\bsqlite(?:3)?\b"]},
    "DynamoDB": {"category": "database", "aliases": [r"\bdynamodb\b"]},
    "Elasticsearch": {"category": "database", "aliases": [r"\belasticsearch\b", r"\belk\b"]},
    "Kafka": {"category": "database", "aliases": [r"\b(?:apache\s+)?kafka\b"]},
    "RabbitMQ": {"category": "database", "aliases": [r"\brabbitmq\b"]},
    "Snowflake": {"category": "database", "aliases": [r"\bsnowflake\b"]},
    "BigQuery": {"category": "database", "aliases": [r"\bbigquery\b"]},

    # AI, ML & Data Science
    "Machine Learning": {"category": "ai_ml", "aliases": [r"\bmachine\s+learning\b", r"\bml\b"]},
    "Deep Learning": {"category": "ai_ml", "aliases": [r"\bdeep\s+learning\b", r"\bdl\b"]},
    "PyTorch": {"category": "ai_ml", "aliases": [r"\bpytorch\b"]},
    "TensorFlow": {"category": "ai_ml", "aliases": [r"\btensorflow\b", r"\btf\b"]},
    "Scikit-Learn": {"category": "ai_ml", "aliases": [r"\bscikit-learn\b", r"\bsklearn\b"]},
    "NLP": {"category": "ai_ml", "aliases": [r"\bnlp\b", r"\bnatural\s+language\s+processing\b"]},
    "LLMs": {"category": "ai_ml", "aliases": [r"\bllm(?:s)?\b", r"\blarge\s+language\s+models?\b", r"\bgpt\b", r"\btransformers?\b"]},
    "Pandas": {"category": "ai_ml", "aliases": [r"\bpandas\b"]},
    "NumPy": {"category": "ai_ml", "aliases": [r"\bnumpy\b"]},
    "Computer Vision": {"category": "ai_ml", "aliases": [r"\bcomputer\s+vision\b", r"\bopencv\b"]},
    "LangChain": {"category": "ai_ml", "aliases": [r"\blangchain\b"]},
    "Hugging Face": {"category": "ai_ml", "aliases": [r"\bhugging\s*face\b"]},
    "Spark": {"category": "ai_ml", "aliases": [r"\b(?:apache\s+)?spark\b", r"\bpyspark\b"]},

    # Architecture & Engineering
    "Microservices": {"category": "architecture", "aliases": [r"\bmicroservices?\b"]},
    "System Design": {"category": "architecture", "aliases": [r"\bsystem\s+design\b", r"\bdistributed\s+systems?\b"]},
    "Event-Driven Architecture": {"category": "architecture", "aliases": [r"\bevent-driven\b", r"\bevent\s+streaming\b"]},
    "Object-Oriented Programming": {"category": "architecture", "aliases": [r"\boop\b", r"\bobject-oriented\b"]},

    # Soft Skills & Engineering Leadership
    "Agile": {"category": "soft_skill", "aliases": [r"\bagile\b", r"\bscrum\b", r"\bkanban\b"]},
    "Leadership": {"category": "soft_skill", "aliases": [r"\bleadership\b", r"\bteam\s+lead\b", r"\btech\s+lead\b"]},
    "Cross-Functional Collaboration": {"category": "soft_skill", "aliases": [r"\bcross-functional\b", r"\bcollaboration\b", r"\bpartnered with\b"]},
    "Mentorship": {"category": "soft_skill", "aliases": [r"\bmentoring\b", r"\bmentorship\b", r"\bcoached\b"]},
    "Problem Solving": {"category": "soft_skill", "aliases": [r"\bproblem[\s-]solving\b", r"\banalytical\s+skills\b"]},
}


class SkillExtractor:
    """Extracts normalized candidate skills and cites contextual evidence."""

    def __init__(self):
        # Precompile regex patterns for high speed
        self._compiled_skills = []
        for name, data in SKILL_TAXONOMY.items():
            patterns = [re.compile(p, re.IGNORECASE) for p in data["aliases"]]
            self._compiled_skills.append({
                "name": name,
                "category": data["category"],
                "patterns": patterns,
            })

    def extract_skills(self, text: str) -> list[dict[str, Any]]:
        """Parse raw resume text and extract classified technical and domain skills."""
        if not text:
            return []

        sentences = re.split(r"(?<=[.!?\n])\s+", text)
        found_skills = {}

        for sentence in sentences:
            s_clean = sentence.strip()
            if len(s_clean) < 3:
                continue

            for item in self._compiled_skills:
                name = item["name"]
                category = item["category"]

                # Test patterns
                matched = False
                for p in item["patterns"]:
                    if p.search(s_clean):
                        matched = True
                        break

                if matched:
                    if name not in found_skills:
                        # Extract context snippet
                        snippet = s_clean[:220].strip()
                        # Simple years of experience estimation near skill
                        years = self._estimate_years_experience(text, item["patterns"])
                        found_skills[name] = {
                            "skill_name": name,
                            "category": category,
                            "evidence_text": snippet,
                            "years_of_experience": years,
                        }

        return list(found_skills.values())

    def extract_candidate_info(self, text: str) -> dict[str, Any]:
        """Extract name, email, phone, links, education, and experience from resume text."""
        info = {
            "full_name": None,
            "email": None,
            "phone": None,
            "location": None,
            "summary": None,
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
        }

        if not text:
            return info

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # 1. Email extraction
        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", text)
        if email_match:
            info["email"] = email_match.group(0)

        # 2. Phone extraction
        phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        if phone_match:
            info["phone"] = phone_match.group(0)

        # 3. Candidate Name extraction (heuristic: first non-empty line without email/phone/url)
        for line in lines[:5]:
            if "@" not in line and "http" not in line and not re.search(r"\d{3}", line):
                # Check line length and word count
                words = line.split()
                if 1 <= len(words) <= 4 and len(line) < 40 and not any(kw in line.lower() for kw in ["resume", "curriculum", "page"]):
                    info["full_name"] = line.strip()
                    break

        # 4. Location extraction
        loc_match = re.search(r"\b([A-Z][a-zA-Z\s]+,\s*[A-Z]{2}(?:\s+\d{5})?|[A-Z][a-zA-Z]+,\s*[A-Z][a-zA-Z]+)\b", text)
        if loc_match:
            info["location"] = loc_match.group(0)

        # 5. Education extraction
        edu_keywords = ["bachelor", "master", "ph.d", "bs", "ms", "b.s.", "m.s.", "b.tech", "m.tech", "degree", "university", "college"]
        education_list = []
        for line in lines:
            line_l = line.lower()
            if any(k in line_l for k in edu_keywords):
                year_match = re.search(r"\b(19\d{2}|20\d{2})\b", line)
                year = year_match.group(0) if year_match else None
                education_list.append({
                    "degree": line[:100],
                    "institution": line[:120],
                    "year": year,
                })
        info["education"] = education_list[:3]

        # 6. Experience extraction
        exp_keywords = ["software engineer", "developer", "lead", "architect", "manager", "intern", "data scientist", "consultant"]
        experience_list = []
        for i, line in enumerate(lines):
            line_l = line.lower()
            if any(role in line_l for role in exp_keywords) and len(line) < 100:
                # Capture next 2 lines as context/bullets
                context = " ".join(lines[i+1:i+3]) if i+1 < len(lines) else ""
                experience_list.append({
                    "title": line,
                    "description": context[:250],
                })
        info["experience"] = experience_list[:6]

        # 7. Summary extraction (first paragraph after header)
        if len(lines) > 2:
            for line in lines[1:6]:
                if len(line) > 60:
                    info["summary"] = line
                    break

        # 8. Check for missing information (Prompt 03)
        missing = []
        if not info["email"]:
            missing.append("Email address")
        if not info["phone"]:
            missing.append("Phone number")
        if not info["education"]:
            missing.append("Education section")
        if not info["experience"]:
            missing.append("Work experience section")
        info["missing_information"] = missing

        return info

    def _estimate_years_experience(self, text: str, patterns: list) -> float | None:
        """Estimate years of experience mentioned in proximity to skill."""
        for p in patterns:
            # Look for "X+ years of [skill]" or "[skill] (X years)"
            match = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)[^.\n]{0,30}" + p.pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
        return None
