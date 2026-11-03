"""AI Interviewer Copilot.

Assists human interviewers by dynamically generating technical interview questions
(Python, SQL, Machine Learning, Generative AI) at Basic, Intermediate, and Advanced
levels, providing follow-up prompts, explaining coding errors, and structuring
evidence-grounded candidate evaluation summaries.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

CURATED_QUESTION_BANK = {
    "python": {
        "basic": [
            {
                "question": "Explain the difference between mutable and immutable data types in Python with concrete examples.",
                "ideal_answer": "Mutable types (lists, dicts, sets) can be altered in-place after creation, modifying their memory content. Immutable types (int, float, str, tuple, frozenset) cannot be modified; any modification creates a new object in memory.",
                "criteria": ["Understands object identity (id())", "Memory implications of mutation", "Function argument default mutable pitfalls"],
                "follow_ups": [
                    "What happens when you pass a mutable object as a default argument in a function definition?",
                    "How does copy.copy() differ from copy.deepcopy() when handling nested mutable collections?",
                ],
            },
            {
                "question": "How do list comprehensions differ from generator expressions in terms of syntax and memory consumption?",
                "ideal_answer": "List comprehensions use brackets [] and evaluate eagerly, storing the entire list in memory. Generator expressions use parentheses () and evaluate lazily using the iterator protocol (yielding values one at a time via __next__), consuming constant O(1) memory.",
                "criteria": ["Memory efficiency", "Lazy vs eager evaluation", "Use of yield and iterators"],
                "follow_ups": [
                    "When would you choose a list comprehension over a generator?",
                    "How would you measure the memory difference between both structures?",
                ],
            },
        ],
        "intermediate": [
            {
                "question": "What is the Global Interpreter Lock (GIL) in CPython, and how does it impact CPU-bound versus I/O-bound concurrency?",
                "ideal_answer": "The GIL is a mutex that prevents multiple native threads from executing Python bytecodes simultaneously in CPython to simplify thread-safe memory management (reference counting). It prevents multi-threaded speedups on CPU-bound tasks (where multiprocessing is preferred), but releases the lock during I/O operations (network, disk, sleep), making threading or asyncio effective for I/O-bound applications.",
                "criteria": ["Understands CPython internals", "Distinguishes CPU vs I/O bound", "Recommends multiprocessing vs asyncio appropriately"],
                "follow_ups": [
                    "What architectural changes are being introduced in Python 3.13 free-threaded builds (PEP 703)?",
                    "How does asyncio achieve concurrency without OS threads?",
                ],
            },
            {
                "question": "Explain how Python decorators work under the hood and how to preserve function metadata using functools.wraps.",
                "ideal_answer": "Decorators are higher-order functions that take a callable as input and return a replacement callable or wrapper closure. Without functools.wraps, the decorated function's __name__, __doc__, and signature are overwritten by the wrapper closure. @wraps copies this introspective metadata back to the wrapper.",
                "criteria": ["Closure understanding", "Higher-order functions", "Importance of functools.wraps"],
                "follow_ups": [
                    "How do you implement a decorator that accepts parameters (e.g., @retry(max_attempts=3))?",
                    "Can a class be used as a decorator?",
                ],
            },
        ],
        "advanced": [
            {
                "question": "Describe Python's garbage collection mechanism, specifically focusing on reference counting and the cyclic garbage collector (generational GC).",
                "ideal_answer": "Python uses reference counting as its primary GC mechanism: each object tracks the count of references to it, and when the count hits zero, deallocation is immediate. To resolve circular references (e.g., object A references B, and B references A), CPython runs a cyclic GC based on three generations (Gen 0, 1, 2) utilizing a doubly-linked list of container objects and detecting unreachable reference cycles.",
                "criteria": ["Reference counting vs cyclic GC", "Generational GC concepts", "Weakref understanding and memory leak debugging"],
                "follow_ups": [
                    "How can the gc module be tuned or disabled in high-throughput microservices?",
                    "How does sys.getrefcount() affect an object's reference counter during inspection?",
                ],
            },
        ],
    },
    "sql": {
        "basic": [
            {
                "question": "What is the difference between WHERE and HAVING clauses in SQL?",
                "ideal_answer": "WHERE filters rows before any groupings or aggregate functions are calculated. HAVING filters aggregated groups after the GROUP BY clause has executed.",
                "criteria": ["Query execution order", "Use of aggregate functions", "Filtering rows vs groups"],
                "follow_ups": [
                    "Can you use HAVING without a GROUP BY clause?",
                    "Why cannot aggregate functions like COUNT() be used directly inside WHERE?",
                ],
            },
        ],
        "intermediate": [
            {
                "question": "Explain SQL Window Functions (e.g., ROW_NUMBER(), RANK(), DENSE_RANK()) and how PARTITION BY works.",
                "ideal_answer": "Window functions perform calculations across a set of table rows related to the current row without collapsing rows like GROUP BY. PARTITION BY divides the result set into distinct partitions, and the ranking function assigns ranks within each partition. ROW_NUMBER gives sequential 1,2,3; RANK skips numbers on ties (1,2,2,4); DENSE_RANK does not skip numbers (1,2,2,3).",
                "criteria": ["Clear distinction between ROW_NUMBER, RANK, and DENSE_RANK", "Role of PARTITION BY vs ORDER BY", "Preservation of row cardinality"],
                "follow_ups": [
                    "How would you retrieve the top 3 highest-earning employees in each department using a window function?",
                    "What is the performance implication of window functions on very large tables?",
                ],
            },
        ],
        "advanced": [
            {
                "question": "How do database indexes (B-Tree vs Hash vs GIN) work, and what causes an index scan to degrade into a sequential scan?",
                "ideal_answer": "B-Tree indexes maintain a balanced tree supporting logarithmic equality and range lookups. Hash indexes only support fast equality. GIN indexes invert documents/arrays for multi-key lookups. An index scan degrades to a sequential table scan when: leading wildcard searches are used (LIKE '%foo'), column values are wrapped in functions (e.g. UPPER(name) without functional index), high selectivity estimates indicate reading the table directly is faster, or table statistics are stale.",
                "criteria": ["Index internal structures", "EXPLAIN / ANALYZE interpretation", "Common index invalidation patterns"],
                "follow_ups": [
                    "What is a covering index and how does index-only scan save disk I/O?",
                    "How do composite indexes leverage the leftmost prefix rule?",
                ],
            },
        ],
    },
    "machine_learning": {
        "basic": [
            {
                "question": "What is the Bias-Variance tradeoff, and how do overfitting and underfitting relate to it?",
                "ideal_answer": "Bias is error from erroneous assumptions in the learning algorithm (high bias leads to underfitting). Variance is error from sensitivity to small fluctuations in training data (high variance leads to overfitting). As model complexity increases, bias decreases while variance increases. The goal is to minimize total generalization error at the optimal complexity balance.",
                "criteria": ["Definitions of bias and variance", "Recognition of underfitting vs overfitting", "Regularization as a remedy"],
                "follow_ups": [
                    "Name three techniques to reduce variance in an overfitted model.",
                    "Why does cross-validation help in diagnosing this tradeoff?",
                ],
            },
        ],
        "intermediate": [
            {
                "question": "When evaluating a classification model on highly imbalanced data (e.g., 99% negative, 1% positive), why is Accuracy misleading, and which metrics should you use instead?",
                "ideal_answer": "Accuracy is misleading because a trivial model predicting only the majority class achieves 99% accuracy while failing to detect any positive instances. Better metrics include Precision (quality of positive predictions), Recall (sensitivity / coverage of true positives), F1-Score (harmonic mean of precision and recall), and PR-AUC (Precision-Recall Area Under Curve).",
                "criteria": ["Explains the accuracy paradox", "Distinguishes Precision vs Recall", "Applies PR-AUC vs ROC-AUC appropriately"],
                "follow_ups": [
                    "In fraud detection or disease screening, would you prioritize Precision or Recall, and why?",
                    "How does SMOTE work for balancing training data?",
                ],
            },
        ],
        "advanced": [
            {
                "question": "Explain the architectural components of the Transformer model (Self-Attention, Multi-Head Attention, Positional Encoding, and Feed-Forward layers).",
                "ideal_answer": "Self-attention computes Attention(Q, K, V) = softmax((Q * K^T) / sqrt(d_k)) * V, enabling each token to attend to all other tokens regardless of distance. Multi-head attention projects queries, keys, and values into multiple subspaces to capture diverse relationship types in parallel. Positional encodings inject sequence order information since self-attention is permutation-invariant. Feed-forward networks process each position independently with non-linear activation.",
                "criteria": ["Self-attention math formulation", "Role of scaled dot-product factor sqrt(d_k)", "Purpose of positional encodings"],
                "follow_ups": [
                    "Why is the dot-product divided by sqrt(d_k)?",
                    "How does FlashAttention optimize the memory and compute overhead of standard self-attention?",
                ],
            },
        ],
    },
    "generative_ai": {
        "basic": [
            {
                "question": "What is Retrieval-Augmented Generation (RAG) and what problem does it solve compared to vanilla LLMs?",
                "ideal_answer": "RAG combines external document retrieval with generative models. Instead of relying solely on parametric knowledge in the LLM's weights, relevant text chunks are retrieved from a vector database based on the query and injected into the prompt context. This reduces hallucinations, provides source attribution/citations, and enables access to private or up-to-date data without expensive fine-tuning.",
                "criteria": ["Parametric vs non-parametric knowledge", "Hallucination mitigation", "Vector search integration"],
                "follow_ups": [
                    "What are the main failure modes in a RAG pipeline?",
                    "How do chunk size and chunk overlap affect retrieval quality?",
                ],
            },
        ],
        "intermediate": [
            {
                "question": "How do embedding models and vector databases perform semantic search using cosine similarity or dot product?",
                "ideal_answer": "Embedding models convert text into dense high-dimensional vectors where semantic proximity corresponds to vector proximity. Cosine similarity measures the cosine of the angle between two normalized vectors (dot product of unit vectors), ranging from -1 to 1. Vector databases build indexing structures like HNSW (Hierarchical Navigable Small World) or IVF (Inverted File Index) to conduct Approximate Nearest Neighbor (ANN) search in sub-linear time.",
                "criteria": ["Dense vector representations", "Cosine similarity vs Euclidean distance", "ANN indexing (HNSW) understanding"],
                "follow_ups": [
                    "Why can't we just do exhaustive k-NN search across 10 million vectors in production?",
                    "What is hybrid search (combining dense vectors with BM25 keyword search)?",
                ],
            },
        ],
        "advanced": [
            {
                "question": "Compare LLM Prompt Engineering, RAG, and Parameter-Efficient Fine-Tuning (PEFT/LoRA). When should an organization choose each strategy?",
                "ideal_answer": "Prompt Engineering is lowest cost/effort, ideal for general tasks without private knowledge. RAG is best when the task requires factual accuracy over dynamic or proprietary documents, citations, and frequent data updates. LoRA/Fine-Tuning is best when modifying the model's style, output structure, reasoning behavior, or learning domain-specific jargon that cannot be taught through few-shot examples.",
                "criteria": ["Clear architectural comparison", "Cost vs latency vs accuracy tradeoffs", "Correct decision framework for engineering leads"],
                "follow_ups": [
                    "How does Low-Rank Adaptation (LoRA) reduce trainable parameter count by freezing base weights and training low-rank decomposition matrices A and B?",
                    "What evaluation frameworks (e.g., Ragas, TruLens) exist to evaluate RAG pipelines in production?",
                ],
            },
        ],
    },
}


class AIInterviewerCopilot:
    """Provides technical interview assistance, question generation, and evidence analysis."""

    def generate_interview_questions(
        self,
        job_title: str,
        category: str = "all",
        difficulty: str = "intermediate",
        skills: Optional[List[str]] = None,
        count: int = 5,
    ) -> List[Dict[str, Any]]:
        """Generate categorized, difficulty-tailored technical interview questions."""
        target_categories = (
            [category.lower()]
            if category.lower() in CURATED_QUESTION_BANK
            else ["python", "sql", "machine_learning", "generative_ai"]
        )

        selected_questions = []

        for cat in target_categories:
            cat_data = CURATED_QUESTION_BANK.get(cat, {})
            pool = []
            if difficulty.lower() in cat_data:
                pool = cat_data[difficulty.lower()]
            else:
                for d in ("basic", "intermediate", "advanced"):
                    pool.extend(cat_data.get(d, []))

            for item in pool:
                selected_questions.append({
                    "category": cat.replace("_", " ").title(),
                    "difficulty": difficulty.title(),
                    "question_text": item["question"],
                    "ideal_answer": item["ideal_answer"],
                    "evaluation_criteria": item["criteria"],
                    "follow_up_questions": item["follow_ups"],
                })

        # Return requested count
        return selected_questions[:count]

    def explain_coding_error(
        self,
        code: str,
        error_message: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """Analyze a coding error and provide pedagogical guidance for interviewers."""
        err_lower = (error_message or "").lower()

        root_cause = "Runtime execution error occurred during test evaluation."
        interviewer_hint = "Ask the candidate to trace through their loop with a small input example on paper or in comments."
        suggested_question = "How would you handle boundary conditions or empty inputs here?"

        if "syntaxerror" in err_lower:
            root_cause = "Syntax Error: Unmatched parenthesis, bracket, or invalid keyword syntax."
            interviewer_hint = "Gently point out line numbers and check if all brackets and indentation levels match."
            suggested_question = "Could you walk me through the closing statements of your main loop?"
        elif "indexerror" in err_lower or "out of range" in err_lower:
            root_cause = "Index Error / Off-by-one: The code attempted to access an array position beyond its length."
            interviewer_hint = "Ask the candidate what the index is when the loop reaches its final iteration."
            suggested_question = "What happens to the pointer index on the very last element of the list?"
        elif "keyerror" in err_lower:
            root_cause = "Key Error: Dictionary lookup failed because the queried key does not exist."
            interviewer_hint = "Remind them about dict.get(key, default) or checking 'if key in dict'."
            suggested_question = "How do you safely query keys in a hash map when they might not be initialized yet?"
        elif "timed out" in err_lower or "timeout" in err_lower:
            root_cause = "Timeout / Infinite Loop: The loop condition never terminates or algorithmic complexity is O(N^2) or higher."
            interviewer_hint = "Ask the candidate what the termination condition is for their while-loop, or discuss time complexity."
            suggested_question = "What is the time complexity of your nested loop, and could a hash map optimize it to O(N)?"

        return {
            "error_summary": error_message or "Execution failed",
            "root_cause_explanation": root_cause,
            "interviewer_hint": interviewer_hint,
            "suggested_follow_up_prompt": suggested_question,
            "recommended_focus": "Algorithmic thinking, clean error recovery, and edge case resilience",
        }

    def generate_interview_summary(
        self,
        candidate_name: str,
        job_title: str,
        ratings: Dict[str, int],
        notes: str = "",
        strengths: Optional[List[str]] = None,
        concerns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Aggregate ratings and qualitative notes into a structured candidate scorecard."""
        avg_rating = sum(ratings.values()) / max(1, len(ratings)) if ratings else 3.0

        if avg_rating >= 4.2:
            recommendation = "Strong Hire"
        elif avg_rating >= 3.5:
            recommendation = "Hire"
        elif avg_rating >= 2.5:
            recommendation = "Weak Hire"
        else:
            recommendation = "No Hire"

        summary_text = (
            f"Candidate {candidate_name} completed technical evaluation for the {job_title} role. "
            f"Overall competency score averaged {avg_rating:.1f}/5.0 across {len(ratings)} evaluated dimensions. "
            + ("Demonstrated strong core foundations and clear communication." if avg_rating >= 3.5 else "Identified gaps in core architecture or execution speed.")
        )

        return {
            "candidate_name": candidate_name,
            "job_title": job_title,
            "average_score": round(avg_rating, 2),
            "recommendation": recommendation,
            "executive_summary": summary_text,
            "dimension_scores": ratings,
            "key_strengths": strengths or ["Solid problem-solving methodology", "Clear verbalization of code intent"],
            "key_concerns": concerns or ["Further depth required on distributed scaling and edge cases"],
            "interviewer_notes": notes,
        }
