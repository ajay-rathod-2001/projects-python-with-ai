"""Unit tests for Technical Assessment, Code Execution Runner, AI Interviewer Copilot, and Auth."""

import pytest


def test_list_and_get_assessment_questions(client):
    """Test retrieving assessment question list and specific question."""
    res = client.get("/api/v1/assessment/questions")
    assert res.status_code == 200
    questions = res.json()
    assert len(questions) >= 3

    first = questions[0]
    assert "id" in first
    assert "title" in first
    assert "slug" in first
    assert "public_test_cases" in first

    # Fetch by ID
    q_res = client.get(f"/api/v1/assessment/questions/{first['id']}")
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert q_data["id"] == first["id"]


def test_code_runner_and_submission(client):
    """Test executing candidate Python code and submitting final assessment."""
    res = client.get("/api/v1/assessment/questions?language=python")
    assert res.status_code == 200
    questions = res.json()
    two_sum = next((q for q in questions if "Two Sum" in q["title"]), questions[0])

    valid_solution = (
        "def solution(nums, target):\n"
        "    seen = {}\n"
        "    for i, n in enumerate(nums):\n"
        "        diff = target - n\n"
        "        if diff in seen:\n"
        "            return [seen[diff], i]\n"
        "        seen[n] = i\n"
        "    return []\n"
    )

    # 1. Test runner (public tests)
    run_res = client.post(
        "/api/v1/assessment/run",
        json={
            "question_id": two_sum["id"],
            "code": valid_solution,
            "language": "python",
        },
    )
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["status"] == "passed", f"ERROR: {run_data.get('error')}"
    assert run_data["score_percentage"] == 100.0
    assert run_data["passed_count"] > 0

    # 2. Test final submission (evaluates public + hidden tests)
    sub_res = client.post(
        "/api/v1/assessment/submit",
        json={
            "question_id": two_sum["id"],
            "candidate_name": "Sarah Connor",
            "candidate_email": "sarah@example.com",
            "code": valid_solution,
            "language": "python",
        },
    )
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert sub_data["status"] == "passed"
    assert sub_data["candidate_name"] == "Sarah Connor"
    assert sub_data["score_percentage"] == 100.0
    assert "ai_analysis" in sub_data


def test_ai_interviewer_copilot(client):
    """Test generating interview questions, explaining errors, and summarizing interviews."""
    # 1. Question generation
    q_res = client.post(
        "/api/v1/interview/generate-questions",
        json={
            "job_title": "Staff Backend Engineer",
            "category": "python",
            "difficulty": "advanced",
            "count": 2,
        },
    )
    assert q_res.status_code == 200
    questions = q_res.json()
    assert len(questions) > 0
    assert "question_text" in questions[0]
    assert "ideal_answer" in questions[0]
    assert len(questions[0]["evaluation_criteria"]) > 0

    # 2. Error explainer
    err_res = client.post(
        "/api/v1/interview/explain-error",
        json={
            "code": "for i in range(len(arr)): print(arr[i+1])",
            "error_message": "IndexError: list index out of range",
            "language": "python",
        },
    )
    assert err_res.status_code == 200
    err_data = err_res.json()
    assert "interviewer_hint" in err_data
    assert "suggested_follow_up_prompt" in err_data

    # 3. Interview summary
    sum_res = client.post(
        "/api/v1/interview/summarize",
        json={
            "candidate_name": "Alex Mercer",
            "job_title": "Senior AI Engineer",
            "ratings": {"algorithms": 5, "system_design": 4, "communication": 5},
            "notes": "Candidate demonstrated deep domain expertise.",
        },
    )
    assert sum_res.status_code == 200
    sum_data = sum_res.json()
    assert sum_data["recommendation"] in ["Strong Hire", "Hire"]
    assert sum_data["average_score"] > 4.0


def test_auth_workflow(client):
    """Test user registration, login, and protected route access."""
    import uuid
    email = f"recruiter_{uuid.uuid4().hex[:8]}@hireai.io"
    password = "SecurePassword123!"

    # 1. Register
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "HireAI Talent Lead",
            "password": password,
            "role": "recruiter",
        },
    )
    assert reg_res.status_code == 200
    token_data = reg_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 2. Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # 3. Protected /me endpoint
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    profile = me_res.json()
    assert profile["email"] == email
    assert profile["full_name"] == "HireAI Talent Lead"
