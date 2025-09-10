import json

def get_coding_judge_instrunction(reviewer_result, code_scores, conv_scores, overall, transcript, feedback):
    prompt = f"""
    You are an interview judge. You have:
    - Reviewer result (tests, compile status, complexity estimates, etc.)
    - Scores (correctness, efficiency, robustness, big-O, edge cases, communication)
    - Transcript (interview Q&A)

    TASK:
    1. Write a clear narrative (2–4 short paragraphs) that combines the code review
    and the transcript evaluation.
    2. Highlight strengths, weaknesses, and whether the candidate’s explanations
    filled gaps in their code.
    3. Give 2–3 actionable next steps.

    Reviewer Result:
    {json.dumps(reviewer_result, indent=2)}

    Scores:
    {json.dumps({"code": code_scores, "conversation": conv_scores, "overall": overall}, indent=2)}

    Transcript:
    {json.dumps(transcript, indent=2)}

    Feedback (bullets):
    {json.dumps(feedback, indent=2)}
    """
    return prompt

def get_system_prompt():
    return """
    You are a coding interview judge.
    Given a problem statement, infer:
    1. The optimal time and space complexity for the most common solution.
    2. At least 3 key edge case categories that should be tested (e.g., empty input, duplicates, large input).
    Return JSON with { "optimal": {...}, "edge_cases": [...] }.
    """

def get_complexity_prompt(description: str, official_solution: str, language: str,  code: str):
    return f"""
    You are a coding interview judge.
    Given a problem description, an official Python reference solution, 
    and a candidate’s solution (which may be in another language such as C++, Java, or JavaScript):

    Problem:
    {description}

    Official Python Solution (reference for optimal complexity):
    {official_solution}

    Candidate Solution (language: {language}):
    {code}

    TASK:
    1. Analyze the official Python solution and infer:
        - Optimal time complexity (e.g., O(n), O(n log n), O(n^2)).
        - Optimal space complexity (e.g., O(n), O(n log n), O(n^2)).
        - 3–4 key edge case categories that should be tested (e.g., empty input, duplicates, large input, negatives).
    2. Analyze the candidate’s code and infer, even if the language is not Python (focus on logic and data structures).:
        - Candidate’s time complexity
        - Candidate’s space complexity
        - Which edge cases their code appears to handle
        - Which edge cases are likely missing
    3. Respond ONLY in this exact JSON format: { ... }.
       Do not include explanations, no markdown, no text outside JSON. Return only strict JSON in this format. 
        {{
            "optimal": {{
                "time": "<complexity>",
                "space": "<complexity>",
                "edge_keywords": ["case1", "case2", "case3"]
            }},
            "candidate": {{
                "time": "<complexity>",
                "space": "<complexity>",
                "edge_covered": ["case1", "case2"],
                "edge_missing": ["caseX", "caseY"]
        }}
        }}
    """


def get_review_prompt(description, official_solution, language, code):
    return f"""
    You are a coding interview judge. You will simulate running candidate code.

    Problem:
    {description}

    Official Python Solution:
    {official_solution}

    Candidate Solution (language: {language}):
    {code}

    TASK:
    1. Generate 3–5 test cases (mix normal + edge cases).
    2. For each test case:
    - Run it mentally on the official solution (expected output).
    - Check if candidate code would likely produce the same output.
    - Mark as "pass" or "fail".
    4. Respond ONLY in this exact JSON format: { ... }.
        Do not include explanations, no markdown, no text outside JSON. Return strict JSON in this format:
        {{
            "compile_status": "ok",
            "tests": [
                {{"name": "case1", "input": "...", "expected": "...", "output": "...", "status": "pass"}},
                ...
            ],
        }}
"""

def get_conversation_score_prompt(description, candidate, transcript, optimal, code_feedback):
    return  f"""
    You are an interview judge.
    You will score how well the candidate explained and defended their code solution
    based on the interview transcript, the problem and the code analysis results.

    Problem:
    {description}

    Transcript:
    {transcript}

    Code Analysis:
    - Candidate actual complexity: time={candidate.get("time")}, space={candidate.get("space")}
    - Optimal complexity: time={optimal.get("time")}, space={optimal.get("space")}
    - Edge cases expected: {optimal.get("edge_keywords", [])}
    - Code feedback: {code_feedback}

    TASK:
    Rate the conversation on:
    1. **Understanding** – Did they correctly understand their own solution’s complexity?
    2. **Awareness** – Did they acknowledge missing edge cases or weaknesses when asked?
    3. **Defense** – Did they justify tradeoffs or design choices clearly?
    4. **Clarity** – Was their explanation structured and easy to follow?

    Respond ONLY in this exact JSON format: { ... }. Do not include explanations, no markdown, no text outside JSON. Return only JSON:
    {{
        "understanding": <0-100>,
        "awareness": <0-100>,
        "defense": <0-100>,
        "clarity": <0-100>,
        "feedback": ["point1","point2",...]
    }}
    """

def get_practice_recommendation(
    code_scores,
    conv_scores,
    code_fb,
    conv_fb
):
    input_data = {
        "code_scores": code_scores,
        "conversation_scores": conv_scores,
        "code_feedback": code_fb,
        "conversation_feedback": conv_fb,
    }
    return f"""
        You are a coding interview coach.

        Below is the candidate’s performance data:

        {json.dumps(input_data, indent=2)}

        Your task:
        1. Look at all categories (both code_scores and conversation_scores).
        2. Select the 3 lowest categories that have a score < 50.
            - If fewer than 3 categories are < 50, include only those.
            - If none are < 50, return an empty JSON object {{}}.
        3. For each selected category, provide 4–5 **concrete, actionable practice suggestions**.
            - Be specific. Avoid generic advice like "study more" or "improve coding".
            - Examples: "Solve 5 LeetCode Easy problems on arrays in one sitting", "Practice explaining O(n log n) sorting algorithms aloud".

        Formatting rules:
        - Output must be valid JSON only.
        - Do not include markdown, explanations, or code fences.
        - Output must start with '{{' and end with '}}'.

        Required format:
        {{
        "CategoryName1": ["practice1", "practice2", "practice3", "practice4"],
        "CategoryName2": ["practice1", "practice2", "practice3", "practice4"]
        }}
    """