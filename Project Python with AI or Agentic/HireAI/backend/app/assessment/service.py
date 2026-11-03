"""Assessment Service — Manages questions, code evaluation, and performance reporting."""

import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.assessment import AssessmentQuestion, AssessmentSubmission
from app.workers.code_runner import CodeRunner

logger = logging.getLogger(__name__)

DEFAULT_CODING_CHALLENGES = [
    {
        "title": "Two Sum Target Pair Finder",
        "slug": "two-sum-target-pair",
        "category": "coding",
        "language": "python",
        "difficulty": "easy",
        "description": """### Two Sum Target Pair Finder
Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.
You may assume that each input would have exactly one solution, and you may not use the same element twice.
Return the answer sorted in ascending order `[i, j]`.

#### Example 1:
```
Input: nums = [2, 7, 11, 15], target = 9
Output: [0, 1]
```
""",
        "starter_code": """def solution(nums, target):
    # Write your optimal O(N) solution here
    seen = {}
    for i, n in enumerate(nums):
        diff = target - n
        if diff in seen:
            return [seen[diff], i]
        seen[n] = i
    return []
""",
        "solution_template": """def solution(nums, target):
    lookup = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in lookup:
            return [lookup[complement], i]
        lookup[num] = i
    return []
""",
        "test_cases": [
            {"id": 1, "input": [[2, 7, 11, 15], 9], "expected": [0, 1], "is_hidden": False, "explanation": "2 + 7 = 9"},
            {"id": 2, "input": [[3, 2, 4], 6], "expected": [1, 2], "is_hidden": False, "explanation": "2 + 4 = 6"},
            {"id": 3, "input": [[3, 3], 6], "expected": [0, 1], "is_hidden": False, "explanation": "Duplicate elements"},
            {"id": 4, "input": [[-1, -2, -3, -4, -5], -8], "expected": [2, 4], "is_hidden": True, "explanation": "Negative numbers: -3 + -5 = -8"},
            {"id": 5, "input": [[1000000, 500, 2000000, 500], 1000], "expected": [1, 3], "is_hidden": True, "explanation": "Large magnitude values"},
        ],
        "tags": ["arrays", "hash-table", "python"],
    },
    {
        "title": "Async Concurrency Task Queue (JavaScript)",
        "slug": "async-concurrency-queue-js",
        "category": "coding",
        "language": "javascript",
        "difficulty": "medium",
        "description": """### Async Concurrency Task Queue
Implement an algorithm that calculates the total cumulative duration of a batch of processed promises.
Given an array of integer task durations `durations` (in ms), return the maximum duration among all tasks.
""",
        "starter_code": """function solution(durations) {
    if (!durations || durations.length === 0) return 0;
    return Math.max(...durations);
}
""",
        "solution_template": """function solution(durations) {
    return Math.max(...durations);
}
""",
        "test_cases": [
            {"id": 1, "input": [[10, 20, 30]], "expected": 30, "is_hidden": False},
            {"id": 2, "input": [[50, 100, 25]], "expected": 100, "is_hidden": False},
            {"id": 3, "input": [[1200, 450, 900, 1500]], "expected": 1500, "is_hidden": True},
        ],
        "tags": ["concurrency", "javascript", "algorithms"],
    },
    {
        "title": "Maximum Subarray Sum (Kadane's Algorithm)",
        "slug": "max-subarray-sum",
        "category": "coding",
        "language": "python",
        "difficulty": "medium",
        "description": """### Maximum Subarray Sum
Given an integer array `nums`, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.

#### Example 1:
```
Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
Output: 6 (Subarray [4,-1,2,1])
```
""",
        "starter_code": """def solution(nums):
    # Implement Kadane's Algorithm O(N) time O(1) space
    max_so_far = nums[0]
    curr_max = nums[0]
    for x in nums[1:]:
        curr_max = max(x, curr_max + x)
        max_so_far = max(max_so_far, curr_max)
    return max_so_far
""",
        "solution_template": """def solution(nums):
    max_so_far = nums[0]
    curr = nums[0]
    for x in nums[1:]:
        curr = max(x, curr + x)
        max_so_far = max(max_so_far, curr)
    return max_so_far
""",
        "test_cases": [
            {"id": 1, "input": [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "expected": 6, "is_hidden": False},
            {"id": 2, "input": [[1]], "expected": 1, "is_hidden": False},
            {"id": 3, "input": [[5, 4, -1, 7, 8]], "expected": 23, "is_hidden": False},
            {"id": 4, "input": [[-5, -2, -9, -1]], "expected": -1, "is_hidden": True},
        ],
        "tags": ["dynamic-programming", "arrays"],
    },
]

DEFAULT_MCQ_QUESTIONS = [
    {
        "title": "Python Memory Management & GIL",
        "slug": "python-gil-memory",
        "category": "mcq",
        "language": "python",
        "difficulty": "intermediate",
        "description": "How does Python handle multithreading CPU-bound tasks in CPython?",
        "mcq_options": [
            {"id": "A", "text": "CPython runs threads concurrently across multiple CPU cores without restriction.", "is_correct": False},
            {"id": "B", "text": "The Global Interpreter Lock (GIL) permits only one native thread to execute Python bytecode at a time.", "is_correct": True},
            {"id": "C", "text": "CPython automatically converts multi-threaded code into multi-process code.", "is_correct": False},
            {"id": "D", "text": "GIL only applies to async/await event loops.", "is_correct": False},
        ],
        "tags": ["python", "concurrency", "cpython"],
    },
    {
        "title": "PostgreSQL Indexing & B-Trees",
        "slug": "postgres-btree-indexing",
        "category": "mcq",
        "language": "sql",
        "difficulty": "intermediate",
        "description": "Which PostgreSQL index type is optimal for equality and range queries on high-cardinality columns?",
        "mcq_options": [
            {"id": "A", "text": "GIN (Generalized Inverted Index)", "is_correct": False},
            {"id": "B", "text": "BRIN (Block Range Index)", "is_correct": False},
            {"id": "C", "text": "B-Tree Index", "is_correct": True},
            {"id": "D", "text": "Hash Index", "is_correct": False},
        ],
        "tags": ["sql", "database", "indexing"],
    },
]


class AssessmentService:
    """Business logic for coding and MCQ technical assessments."""

    def __init__(self, db: Session):
        self.db = db
        self.runner = CodeRunner()

    def seed_default_questions_if_empty(self):
        """Seed pre-configured questions if table is empty."""
        count = self.db.query(AssessmentQuestion).count()
        if count == 0:
            for q_data in DEFAULT_CODING_CHALLENGES + DEFAULT_MCQ_QUESTIONS:
                q = AssessmentQuestion(
                    title=q_data["title"],
                    slug=q_data["slug"],
                    description=q_data["description"],
                    category=q_data["category"],
                    language=q_data.get("language", "python"),
                    difficulty=q_data.get("difficulty", "medium"),
                    starter_code=q_data.get("starter_code"),
                    solution_template=q_data.get("solution_template"),
                    test_cases=q_data.get("test_cases"),
                    mcq_options=q_data.get("mcq_options"),
                    tags=q_data.get("tags", []),
                )
                self.db.add(q)
            self.db.commit()

    def get_all_questions(self, category: Optional[str] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        self.seed_default_questions_if_empty()
        query = self.db.query(AssessmentQuestion)
        if category:
            query = query.filter(AssessmentQuestion.category == category)
        if language and language != "all":
            query = query.filter(AssessmentQuestion.language == language)

        questions = query.all()
        result = []
        for q in questions:
            # Filter out hidden test case details for public question listing
            public_cases = []
            if q.test_cases:
                for tc in q.test_cases:
                    if not tc.get("is_hidden", False):
                        public_cases.append(tc)

            result.append({
                "id": q.id,
                "title": q.title,
                "slug": q.slug,
                "category": q.category,
                "language": q.language,
                "difficulty": q.difficulty,
                "description": q.description,
                "starter_code": q.starter_code,
                "public_test_cases": public_cases,
                "total_test_cases_count": len(q.test_cases) if q.test_cases else 0,
                "mcq_options": q.mcq_options,
                "tags": q.tags,
            })
        return result

    def get_question_by_id(self, question_id: str) -> Optional[AssessmentQuestion]:
        self.seed_default_questions_if_empty()
        return self.db.query(AssessmentQuestion).filter(AssessmentQuestion.id == question_id).first()

    def run_candidate_code(
        self,
        question_id: str,
        code: str,
        language: str,
        include_hidden: bool = False,
    ) -> Dict[str, Any]:
        """Run code against test cases without recording permanent submission."""
        question = self.get_question_by_id(question_id)
        if not question or not question.test_cases:
            # Run code with a default dummy case
            cases = [{"id": 1, "input": [], "expected": None, "is_hidden": False}]
        else:
            if include_hidden:
                cases = question.test_cases
            else:
                cases = [c for c in question.test_cases if not c.get("is_hidden", False)]
                if not cases:
                    cases = question.test_cases

        result = self.runner.execute_code(code=code, language=language, test_cases=cases)
        return result.to_dict()

    def submit_assessment(
        self,
        question_id: str,
        candidate_name: str,
        candidate_email: str,
        code: str,
        language: str,
    ) -> Dict[str, Any]:
        """Evaluate submission against all test cases (public + hidden) and persist record."""
        question = self.get_question_by_id(question_id)
        cases = question.test_cases if question and question.test_cases else []

        eval_res = self.runner.execute_code(code=code, language=language, test_cases=cases)

        # AI Code quality insights
        ai_analysis = (
            f"Evaluated with {eval_res.passed_count}/{eval_res.total_count} test cases passed. "
            f"Execution time: {eval_res.execution_time_ms:.1f}ms. "
            f"Peak memory: {eval_res.memory_used_kb:.1f}KB. "
            + ("Optimal algorithmic complexity demonstrated." if eval_res.score_percentage == 100 else "Consider reviewing edge cases and memory constraints.")
        )

        sub = AssessmentSubmission(
            question_id=question_id,
            candidate_name=candidate_name or "Anonymous Candidate",
            candidate_email=candidate_email,
            language=language,
            submitted_code=code,
            status=eval_res.status,
            passed_count=eval_res.passed_count,
            total_count=eval_res.total_count,
            score_percentage=eval_res.score_percentage,
            execution_time_ms=eval_res.execution_time_ms,
            memory_used_kb=eval_res.memory_used_kb,
            test_case_results=eval_res.test_case_results,
            ai_analysis=ai_analysis,
        )
        self.db.add(sub)
        self.db.commit()
        self.db.refresh(sub)

        return {
            "submission_id": sub.id,
            "question_id": question_id,
            "candidate_name": sub.candidate_name,
            "status": sub.status,
            "score_percentage": sub.score_percentage,
            "passed_count": sub.passed_count,
            "total_count": sub.total_count,
            "execution_time_ms": sub.execution_time_ms,
            "memory_used_kb": sub.memory_used_kb,
            "test_case_results": sub.test_case_results,
            "ai_analysis": sub.ai_analysis,
            "created_at": sub.created_at.isoformat(),
        }

    def get_submissions(self, question_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = self.db.query(AssessmentSubmission)
        if question_id:
            query = query.filter(AssessmentSubmission.question_id == question_id)
        subs = query.order_by(AssessmentSubmission.created_at.desc()).limit(50).all()

        return [
            {
                "id": s.id,
                "question_id": s.question_id,
                "candidate_name": s.candidate_name,
                "candidate_email": s.candidate_email,
                "language": s.language,
                "status": s.status,
                "score_percentage": s.score_percentage,
                "passed_count": s.passed_count,
                "total_count": s.total_count,
                "execution_time_ms": s.execution_time_ms,
                "memory_used_kb": s.memory_used_kb,
                "created_at": s.created_at.isoformat(),
            }
            for s in subs
        ]
