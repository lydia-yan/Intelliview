# tests/test_coding_judge.py
import pytest
import os

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Skipping Firestore-dependent tests in CI"
)
from backend.agents.coding_judge.agent import (
    _bigo_similarity,
    _efficiency_components,
    _score_code,
    _aggregate_scores,
    _compose_feedback,
)

def test_bigo_similarity_exact():
    assert _bigo_similarity("O(n)", "O(n)") == 1.0

def test_bigo_similarity_near():
    assert _bigo_similarity("O(n)", "O(n log n)") == 0.7

def test_efficiency_components():
    parts, fb = _efficiency_components("O(n)", "O(1)", "O(n)", "O(1)", "O(n)", "O(1)")
    assert parts["claim_vs_actual"]["time"] == 100
    assert parts["actual_vs_optimal"]["space"] == 100
    assert fb == []

def test_score_code_compile_error():
    reviewer = {"compile_status": "error", "tests": []}
    optimal = {"time": "O(n)", "space": "O(1)"}
    candidate = {}
    scores, fb = _score_code(reviewer, optimal, candidate)
    assert scores["correctness"] == 0.0
    assert "Code did not compile/run" in fb[0]

def test_aggregate_scores_combines_code_and_conversation():
    code_scores = {
        "correctness": 80,
        "efficiency": 90,
        "robustness": 70,
        "style": 60,
    }
    conv_scores = {
        "understanding": 50,
        "awareness": 40,
        "defense": 30,
        "clarity": 20,
    }
    result = _aggregate_scores(code_scores, conv_scores)

    assert "overall" in result
    assert isinstance(result["overall"], float)
    assert "breakdown" in result
    assert "code" in result["breakdown"]
    assert "conversation" in result["breakdown"]

def test_compose_feedback_strength_and_opportunity():
    code_scores = {"correctness": 10, "efficiency": 90, "robustness": 50, "style": 80}
    conv_scores = {"understanding": 20, "awareness": 30, "defense": 40, "clarity": 25}
    code_fb = ["Test code feedback"]
    conv_fb = ["Test conversation feedback"]

    result = _compose_feedback(code_scores, conv_scores, code_fb, conv_fb)

    assert "strength" in result
    assert "opportunity" in result
