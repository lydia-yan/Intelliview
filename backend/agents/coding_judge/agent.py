# coding_judge.py
from __future__ import annotations
import re, math
from typing import Dict, Any, List, Tuple
import json
import os
import asyncio
import sys
import re
import requests
import subprocess
import tempfile
from duckduckgo_search import DDGS
import time



# Add the project root to the Python path if necessary
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Import unified config
from backend.config import set_google_cloud_env_vars

# Load environment variables
set_google_cloud_env_vars()

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.genai import types
from backend.data.database import firestore_db
from backend.data.schemas import CodingReview
from backend.coordinator.session_manager import session_service
from .prompt import get_complexity_prompt, get_review_prompt, get_conversation_score_prompt, get_practice_recommendation


CODE_JUDGE_AGENT = LlmAgent(
    model="gemini-2.0-flash",
    name="coding_feedback_generator",
    description="Judge coding solutions and combine with transcript into holistic feedback",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2, max_output_tokens=600
    ),
)

AGGREGATION_WEIGHTS = {
    # Code (70%)
    "correctness":   0.35,
    "efficiency":    0.20,
    "robustness":    0.10,
    "style":         0.05,
    # Conversation (30%)
    "understanding": 0.10,
    "awareness":     0.10,
    "defense":       0.05,
    "clarity":       0.05,
}

def run_judge_from_session(session):
    """
    Evaluate an interview by running the InterviewJudgeAgent using an existing session.

    Args:
        session_service: The session service managing state (e.g., InMemorySessionService).
        session_id (str): ID of the session with the context already set.

    Returns:
        dict: JSON feedback from the judge agent.
    """
    return asyncio.run(_run_coding_judge_from_session(session))


# ---------------------------
# Public entry
# ---------------------------

async def _run_coding_judge_from_session(session) -> Dict[str, Any]:
    """
    Returns a single JSON with subscores, overall score, and feedback.
    """
    # each session has its own agent
    runner = Runner(
        agent=CODE_JUDGE_AGENT,
        app_name=session.app_name,
        session_service=session_service
    )
    problem = session.state.get("problem", {})
    claims = {
        "claimed_time": session.state.get("claimed_time"),
        "claimed_space": session.state.get("claimed_space"),
    }
    transcript = session.state.get("transcript", [])
    code = session.state.get("code")
    language = session.state.get("language")

    

    # --- 1) CODE SCORES ---
    complexity_info = await _infer_complexity_and_edges(
        runner, session, problem.get("statement"), problem.get("solutions").get("python"), language, code
    )
    optimal = complexity_info.get("optimal", {})
    candidate = complexity_info.get("candidate", {})

    # FIX
    reviewer_result = await _run_ai_reviewer(
        runner, session, problem.get("statement"), problem.get("solutions").get("python"), language, code
    )
    code_scores, code_feedback = _score_code(code, reviewer_result, optimal, candidate, claims)

    # --- 2) CONVERSATION SCORES ---
    conv_scores, conv_feedback = await _score_conversation(
        runner,
        session,
        problem.get("statement"),
        candidate=candidate,
        transcript=transcript,
        optimal=optimal,
        code_feedback=code_feedback,
    )

    # --- 3) FINAL AGGREGATION ---
    overall = _aggregate_scores(code_scores, conv_scores)

    # --- 4) FEEDBACK ---
    summary = _compose_feedback(code_scores, conv_scores, code_feedback, conv_feedback)
    recommendation = await _ai_practice_improvements(runner, session, code_scores, conv_scores, code_feedback, conv_feedback)

    result = {
        "problem_slug": problem.get("slug"),
        "scores": {
            "overall": overall["overall"],     # just the float
            "code_score": code_scores,
            "conversation_score": conv_scores,
        },
        "feedback": {
            "code": code_feedback,
            "conversation": conv_feedback,
            "strength": summary["strength"],
            "opportunity": summary["opportunity"],
            "next_step": recommendation,
        },
        "reviewer_result": reviewer_result,  # keep raw for auditability
        "optimal_complexity": optimal,
        "transcript": transcript,
    }
    res = save_coding_review_to_db(session, result)
    if "successfully" in res["message"]: 
        print("[DEBUG] CodingReview stored.")
    else:
        print("[ERROR] Coding Review failed to store")
    return result


# assume the json input
def save_coding_review_to_db(session, data):
    """
    Save a Feedback object to Firestore under a specific user and session.

    Args:
        user_id (str): The ID of the user (can be 'user' or UID if you have auth).
        session_id (str): The session ID this Coding Review relates to.
        review (CodingReview): Validated CodingReview object (Pydantic).
    """
    
    return firestore_db.set_coding_review(session.user_id, session.id, CodingReview(**data))




# Optimal complexity lookup
async def _infer_complexity_and_edges(
    runner, session, description: str, official_solution: str, language: str, code: str
) -> Dict[str, Any]:
    prompt = get_complexity_prompt(description, official_solution, language, code)
    content = types.Content(role="user", parts=[types.Part(text=prompt)])
    try:
        response_text = None
        async for event in runner.run_async(
            user_id=session.user_id,  # or session.user_id if available
            session_id=session.id,
            new_message=content
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text
                break
        if not response_text:
            raise ValueError("No response from runner")
        return _force_json(response_text)
    except Exception as e:
        print(f"[ERROR] Complexity inference failed: {e}")
        # Fallback to safe defaults
        return {
            "optimal": {"time": "O(n)", "space": "O(1)", "edge_keywords": []},
            "candidate": {"time": "O(n)", "space": "O(1)", "edge_covered": [], "edge_missing": []},
        }

# Use AI to act as a sandbox reviewer:
async def _run_ai_reviewer(runner,session, description: str, official_solution: str, language: str, code: str) -> Dict[str, Any]:
    prompt = get_review_prompt(description,official_solution, language, code)
    content = types.Content(role="user", parts=[types.Part(text=prompt)])
    try:
        response_text = None
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text
                break
        if not response_text:
            raise ValueError("No reviewer response")
        return _force_json(response_text)
    except Exception as e:
        print(f"[ERROR] AI reviewer failed: {e}")
        return {
            "compile_status": "error",
            "tests": [],
        }

def _score_code(
    code: str,
    reviewer: Dict[str, Any],
    optimal: Dict[str, str],
    candidate: Dict[str, Any],
    claims: Dict[str, Any] | None = None,
) -> Tuple[Dict[str, float], List[str]]:
    """
    reviewer:  from AI reviewer (compile_status, tests[], complexity{estimated_*} optional)
    optimal:   {"time","space"} from official solution (AI-inferred)
    candidate: {"time","space","edge_covered":[...],"edge_missing":[...]} (AI-inferred)
    claims:    {"claimed_time","claimed_space"} from user (explicit claim)
    """
    fb: List[str] = []

    # ---------- Correctness ----------
    tests = reviewer.get("tests", []) or []
    compile_status = (reviewer.get("compile_status") or "error").lower()

    if compile_status != "ok":
        correctness = 0.0
        fb.append("Code did not compile/run; correctness is 0.")
        passed = 0
    else:
        total = max(1, len(tests))
        passed = sum(1 for t in tests if (t.get("status") or "").lower() == "pass")
        correctness = round(100.0 * (passed / total), 1)
        if passed < total:
            failed = [t.get("name") or f"test_{i}" for i, t in enumerate(tests) if (t.get("status") or "").lower() != "pass"]
            fb.append(f"Failed tests: {', '.join(failed)}")

    # ---------- Efficiency (claim↔actual and actual↔optimal) ----------
    # actual from candidate (preferred) then reviewer estimate
    actual_time  = candidate.get("time")  or reviewer.get("complexity", {}).get("estimated_time")  or ""
    actual_space = candidate.get("space") or reviewer.get("complexity", {}).get("estimated_space") or ""
    claim_time   = (claims or {}).get("claimed_time")  or ""
    claim_space  = (claims or {}).get("claimed_space") or ""
    optimal_time  = optimal.get("time")  or ""
    optimal_space = optimal.get("space") or ""

    eff_parts, eff_fb = _efficiency_components(
        claim_time, claim_space, actual_time, actual_space, optimal_time, optimal_space
    )
    fb.extend(eff_fb)

    # Aggregate efficiency:
    #  - time more important than space (0.7/0.3)
    #  - claim-vs-actual and actual-vs-optimal equally weighted (0.5/0.5)
    cva_time = eff_parts["claim_vs_actual"]["time"]
    cva_space = eff_parts["claim_vs_actual"]["space"]
    avo_time = eff_parts["actual_vs_optimal"]["time"]
    avo_space = eff_parts["actual_vs_optimal"]["space"]

    claim_alignment = 0.7 * cva_time + 0.3 * cva_space
    optimal_alignment = 0.7 * avo_time + 0.3 * avo_space
    efficiency = round(0.5 * claim_alignment + 0.5 * optimal_alignment, 1)

    # Soft penalty if many tests fail (overstated complexity claims)
    if compile_status == "ok" and len(tests) >= 3:
        fail_ratio = 1.0 - (passed / max(1, len(tests)))
        if fail_ratio >= 0.34:  # ≥1/3 failed
            drop = min(20.0, 100.0 * fail_ratio * 0.4)
            efficiency = max(0.0, round(efficiency - drop, 1))
            fb.append(f"Efficiency confidence reduced due to failed tests (−{drop:.0f}).")

    # ---------- Robustness ----------
    edge_cov = list(candidate.get("edge_covered") or [])
    edge_miss = list(candidate.get("edge_missing") or [])
    if edge_cov or edge_miss:
        total_edges = max(1, len(edge_cov) + len(edge_miss))
        robustness = round(100.0 * (len(edge_cov) / total_edges), 1)
        if edge_miss:
            fb.append(f"Missing edge cases: {', '.join(edge_miss)}")
    else:
        # fallback to any tests that look like edges
        edge_tests = [t for t in tests if (t.get("name") or "").lower().startswith("edge")]
        if not edge_tests:
            robustness = 50.0
            fb.append("Unable to determine edge coverage; assuming neutral robustness.")
        else:
            edge_total = len(edge_tests)
            edge_passed = sum(1 for t in edge_tests if (t.get("status") or "").lower() == "pass")
            robustness = round(100.0 * (edge_passed / max(1, edge_total)), 1)
            if edge_passed < edge_total:
                failed_edges = [t.get("name") for t in edge_tests if (t.get("status") or "").lower() != "pass"]
                fb.append(f"Edge test failures: {', '.join(failed_edges)}")

    # ---------- Style (placeholder) ----------
    style = score_with_pylint(code)

    scores = {
        "correctness": correctness,
        "efficiency":  efficiency,
        "robustness":  robustness,
        "style":       style,
        "efficiency_breakdown": {
            "claim_vs_actual": {"time": cva_time, "space": cva_space},
            "actual_vs_optimal": {"time": avo_time, "space": avo_space},
        },
    }
    return scores, fb

async def _score_conversation(runner, session, description, candidate, transcript, optimal, code_feedback):
    prompt = get_conversation_score_prompt(description, candidate, transcript, optimal, code_feedback)
    content = types.Content(role="user", parts=[types.Part(text=prompt)])
    try:
        response_text = None
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text
                break
        if not response_text:
            raise ValueError("No conversation scoring response")
        data = _force_json(response_text)
        scores = {
            "understanding": data.get("understanding", 0),
            "awareness": data.get("awareness", 0),
            "defense": data.get("defense", 0),
            "clarity": data.get("clarity", 0),
        }
        return scores, data.get("feedback", [])
    except Exception as e:
        print(f"[ERROR] Conversation scoring failed: {e}")
        return {
            "understanding": 50,
            "awareness": 50,
            "defense": 50,
            "clarity": 50,
        }, ["Fallback conversation score (AI error)"]


# Aggregate & summarize
def _aggregate_scores(
    code_scores: Dict[str, float],
    conv_scores: Dict[str, float],
    weights: Dict[str, float] = AGGREGATION_WEIGHTS,
) -> Dict[str, Any]:
    """
    Combine code + conversation scores into an overall score using AGGREGATION_WEIGHTS.
    """
    overall = 0.0
    for k, w in weights.items():
        if k in code_scores:
            overall += w * code_scores[k]
        elif k in conv_scores:
            overall += w * conv_scores[k]

    return {
        "overall": round(overall, 1),
    }

async def _ai_practice_improvements(
    runner,
    session,
    code_scores: Dict[str, float],
    conv_scores: Dict[str, float],
    code_fb: List[str],
    conv_fb: List[str],
) -> Dict[str, List[str]]:
    """
    Use AI to generate 4-5 specific practice improvements for weak categories.
    Returns {category: [improvement1, improvement2, ...]}.
    """
    prompt = get_practice_recommendation(code_scores, conv_scores, code_fb, conv_fb)

    content = types.Content(role="user", parts=[types.Part(text=prompt)])
    try:
        response_text = None
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text
                break

        if not response_text:
            raise ValueError("No AI improvement response")

        result = _force_json(response_text)
        if not result:
            return {
                "General": [
                    "Review your weakest categories and practice problems step by step.",
                    "Write down edge cases before coding.",
                    "Explain your solution aloud to improve clarity.",
                    "Try optimizing code by replacing nested loops with hash maps.",
                ]
            }
        return result
    except Exception as e:
        print(f"[ERROR] AI practice improvement failed: {e}")
        return {}

def _compose_feedback(
    code_scores: Dict[str, float],
    conv_scores: Dict[str, float],
    code_fb: List[str],
    conv_fb: List[str],
) -> Dict[str, Any]:
    """
    Combine code + conversation feedback into a structured message.
    """
    feedback = {}

    # --- Strengths ---
    best = max(
        [
            ("Correctness", code_scores.get("correctness", 0)),
            ("Efficiency", code_scores.get("efficiency", 0)),
            ("Robustness", code_scores.get("robustness", 0)),
            ("Style", code_scores.get("style", 0)),
            ("Understanding", conv_scores.get("understanding", 0)),
            ("Awareness", conv_scores.get("awareness", 0)),
            ("Defense", conv_scores.get("defense", 0)),
            ("Clarity", conv_scores.get("clarity", 0)),
        ],
        key=lambda x: x[1],
    )
    feedback["strength"] = f"Strongest area: {best[0]} ({best[1]:.1f})."

    # --- Opportunities ---
    worst = min(
        [
            ("Correctness", code_scores.get("correctness", 0)),
            ("Efficiency", code_scores.get("efficiency", 0)),
            ("Robustness", code_scores.get("robustness", 0)),
            ("Style", code_scores.get("style", 0)),
            ("Understanding", conv_scores.get("understanding", 0)),
            ("Awareness", conv_scores.get("awareness", 0)),
            ("Defense", conv_scores.get("defense", 0)),
            ("Clarity", conv_scores.get("clarity", 0)),
        ],
        key=lambda x: x[1],
    )
    feedback["opportunity"] = f"Biggest opportunity: {worst[0]} ({worst[1]:.1f})."

    return feedback

# Helper for code scoring
def _norm_bigo(s: str) -> str:
    """Normalize Big-O strings like 'O( n log n )' -> 'o(nlogn)' for easier matching."""
    if not s:
        return ""
    s = s.strip().lower()
    s = s.replace(" ", "")
    # common variants
    s = s.replace("log(n)", "logn").replace("log(n)", "logn").replace("log(n)", "logn")
    s = s.replace("log2n", "logn").replace("log10n", "logn")
    # ensure leading 'o(' ... ')'
    if not s.startswith("o("):
        # accept raw forms like 'nlogn', 'n^2'
        if re.match(r"^[a-z0-9\^\*]+$", s):
            s = f"o({s})"
        elif re.match(r"^o\(.+\)$", s) is None:
            s = f"o({s})"
    # canonicalize n^2 -> n2
    s = s.replace("^2", "2").replace("^3", "3")
    return s

def _bigo_family(s: str) -> str:
    """Collapse Big-O to families for fuzzy match: o(1), o(logn), o(n), o(nlogn), o(n2), o(n3), o(2n) etc."""
    s = _norm_bigo(s)
    # simple canonical buckets
    if "o(1)" in s:
        return "o(1)"
    if "logn" in s and "nlogn" not in s and "n" not in s:
        return "o(logn)"
    if "nlogn" in s:
        return "o(nlogn)"
    if "n2" in s:
        return "o(n2)"
    if "n3" in s:
        return "o(n3)"
    if "2n" in s or "k*n" in s or "nk" in s:
        return "o(n)"  # treat linear-with-constant/multiplier as linear
    if "n" in s:
        return "o(n)"
    return s  # fallback (o(n^k) will stay distinct but normalized)

def _bigo_similarity(a: str, b: str) -> float:
    """
    Similarity between Big-O strings in [0,1].
    exact=1.0, same family=0.9, near (n vs nlogn or n vs n2)=0.7, else 0.3.
    """
    if not a or not b:
        return 0.0
    an = _norm_bigo(a); bn = _norm_bigo(b)
    if an == bn:
        return 1.0
    af = _bigo_family(an); bf = _bigo_family(bn)
    if af == bf:
        return 0.9
    near_pairs = {("o(n)","o(nlogn)"), ("o(nlogn)","o(n)"), ("o(n)","o(n2)"), ("o(n2)","o(n)")}
    if (af, bf) in near_pairs or (bf, af) in near_pairs:
        return 0.7
    return 0.3

def _efficiency_components(
    claim_time:str, claim_space:str,
    actual_time:str, actual_space:str,
    optimal_time:str, optimal_space:str
):
    """
    Returns per-dimension alignments (0..100) and human feedback.
    """
    fb = []

    # claim vs actual
    cva_t = _bigo_similarity(claim_time,  actual_time)  * 100.0
    cva_s = _bigo_similarity(claim_space, actual_space) * 100.0
    if cva_t < 100:
        fb.append(f"Claim vs actual (time) differs: claimed {claim_time or 'N/A'} vs actual {actual_time or 'N/A'}.")
    if cva_s < 100:
        fb.append(f"Claim vs actual (space) differs: claimed {claim_space or 'N/A'} vs actual {actual_space or 'N/A'}.")

    # actual vs optimal
    avo_t = _bigo_similarity(actual_time,  optimal_time)  * 100.0
    avo_s = _bigo_similarity(actual_space, optimal_space) * 100.0
    if avo_t < 100:
        fb.append(f"Actual vs optimal (time) gap: actual {actual_time or 'N/A'} vs optimal {optimal_time or 'N/A'}.")
    if avo_s < 100:
        fb.append(f"Actual vs optimal (space) gap: actual {actual_space or 'N/A'} vs optimal {optimal_space or 'N/A'}.")

    return {
        "claim_vs_actual": {"time": round(cva_t,1), "space": round(cva_s,1)},
        "actual_vs_optimal": {"time": round(avo_t,1), "space": round(avo_s,1)},
    }, fb

def _force_json(text: str):
    """Extract and parse JSON from LLM output safely."""
    if not text:
        return {}

    # Remove code fences if present
    if "```" in text:
        # take the middle part
        text = re.sub(r"```(json)?", "", text).strip()

    # Try to find JSON object in the string
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        text = match.group(0)

    try:
        return json.loads(text)
    except Exception as e:
        print(f"[ERROR] Failed to parse JSON: {e}\nRaw output: {text}")
        return {}
    
def score_with_pylint(code: str) -> float:
    """Run pylint on given code and return style score (0–100)."""
    # Create a unique temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(code.encode("utf-8"))
        tmp_filename = tmp.name

    try:
        result = subprocess.run(
            ["pylint", "--score=y", "--disable=all", "--enable=convention,refactor", tmp_filename],
            capture_output=True, text=True
        )

        for line in result.stdout.splitlines():
            if "rated at" in line:
                try:
                    score = float(line.split("rated at")[1].split("/")[0])
                    return round(score * 10, 1)  # scale to 0–100
                except Exception:
                    pass
        return 50.0  # fallback neutral
    finally:
        # Clean up temp file
        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)