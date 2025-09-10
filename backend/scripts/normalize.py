import json
import re
import argparse
import os
from typing import Any, Dict, List, Optional, Tuple

try:
    from bs4 import BeautifulSoup  # type: ignore

    BS4_AVAILABLE = True
except Exception:
    BS4_AVAILABLE = False


def _looks_like_html(s: str) -> bool:
    if not isinstance(s, str) or not s:
        return False
    # has tags or common entities
    if "<" in s and ">" in s:
        return True
    if "&" in s and ";" in s:
        return True
    return False

def _maybe_read_file(s: str) -> str:
    # if s is a real file path, read it; otherwise return s
    try:
        if isinstance(s, str) and os.path.isfile(s):
            with open(s, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        pass
    return s


def clean_html_to_text(raw_html: str) -> str:
    """Remove HTML and condense whitespace to plain text."""
    if not raw_html:
        return ""
    s = _maybe_read_file(raw_html)
    if not _looks_like_html(s):
        # treat as plain text
        text = str(s)
    else:
        if BS4_AVAILABLE:
            soup = BeautifulSoup(raw_html, "html.parser")
            # convert <sup>n</sup> to ^n
            for sup in soup.find_all("sup"):
                sup.replace_with("^" + (sup.get_text() or "").strip())
            text = soup.get_text("\n")
        else:
            # Fallback: strip tags with a very rough regex
            text = re.sub(
                r"<sup>\s*(.*?)\s*</sup>", r"^\1", raw_html, flags=re.IGNORECASE | re.DOTALL
            )
            text = re.sub(r"<[^>]+>", " ", text)
        # condense blank lines
        text = re.sub(r"\n\s*\n", "\n", text)
        # collapse spaces on each line
        text = "\n".join(line.strip() for line in text.splitlines())
    return text.strip()


def extract_constraints_preserve_sup(raw_html: str) -> List[str]:
    """
    Extract constraints with exponents preserved inline (10^4, 10^9, etc.)
    """
    text = html_to_text_with_sup_inline(raw_html)

    # Isolate constraints section
    m = re.search(r"Constraints:\s*(.*)", text, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return []
    block = re.split(r"Follow-up:", m.group(1), flags=re.IGNORECASE)[0]

    constraints = []
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^[\-\*\u2022]\s*", "", line)
        constraints.append(line)
    return constraints


def html_to_text_with_sup_inline(raw_html: str) -> str:
    """
    Convert HTML to plain text while merging <sup> inline with preceding number.
    Ensures no duplication: "10<sup>4</sup>" -> "10^4"
    """
    if not raw_html:
        return ""
    s = _maybe_read_file(raw_html)

    if not _looks_like_html(s):
        return str(s).strip()

    if not BS4_AVAILABLE:
        return re.sub(r"<sup>(.*?)</sup>", r"^\1", re.sub(r"<[^>]+>", " ", raw_html))

    soup = BeautifulSoup(raw_html, "html.parser")

    def walk(node) -> str:
        parts = []
        for child in node.children:
            if getattr(child, "name", None) == "sup":
                parts.append("^" + child.get_text(strip=True))
            elif getattr(child, "name", None):  # tag but not sup
                parts.append(walk(child))
            else:  # NavigableString
                parts.append(str(child))
        return "".join(parts)

    return walk(soup)


def parse_examples_from_text(desc_text: str) -> List[Dict[str, str]]:
    """
    Try to capture example blocks with Input/Output/Explanation.
    Very heuristic, but works for most LC descriptions.
    """
    examples: List[Dict[str, str]] = []
    pattern = re.compile(
        r"Input:\s*(.*?)\s*Output:\s*(.*?)(?:\s*Explanation:\s*(.*?))?(?=(?:\n[A-Z][a-z]+:|\Z))",
        re.DOTALL,
    )
    for m in pattern.finditer(desc_text + "\n"):
        input_part = m.group(1).strip()
        output_part = m.group(2).strip()
        explanation = (m.group(3) or "").strip()
        examples.append(
            {"input": input_part, "output": output_part, "explanation": explanation}
        )
    return examples


def parse_constraints(desc_text: str) -> List[str]:
    """
    Pull constraints bullet list if present.
    """
    constraints: List[str] = []

    cons_match = re.search(r"Constraints:\s*(.*?)(?:\n\s*\n|$)", desc_text, re.DOTALL)
    if cons_match:
        raw_block = cons_match.group(1).strip()
        for line in raw_block.splitlines():
            line = line.strip()
            if not line:
                continue
            line = re.sub(r"^[\-\*\u2022]\s*", "", line)
            constraints.append(line)

    return constraints


def parse_stats(stats_field: Any, acceptance_rate: Optional[float]) -> Dict[str, Any]:
    """
    stats can be a JSON string or dict with totalAcceptedRaw, totalSubmissionRaw, acRate.
    """
    accepted = submissions = None
    ac_rate = acceptance_rate
    if isinstance(stats_field, str):
        try:
            stats_obj = json.loads(stats_field)
        except Exception:
            stats_obj = {}
    elif isinstance(stats_field, dict):
        stats_obj = stats_field
    else:
        stats_obj = {}

    if "totalAcceptedRaw" in stats_obj:
        accepted = stats_obj.get("totalAcceptedRaw")

    if "totalSubmissionRaw" in stats_obj:
        submissions = stats_obj.get("totalSubmissionRaw")

    if ac_rate is None and "acRate" in stats_obj:
        try:
            ac_rate = float(str(stats_obj.get("acRate")).replace("%", "").strip())
        except Exception:
            pass

    return {
        "acceptance_rate": round(ac_rate, 2)
        if isinstance(ac_rate, (int, float))
        else ac_rate,
        "submissions": submissions,
        "accepted": accepted,
    }


def extract_complexities_from_solution_text(
    solution_html: str,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Try to find 'Time complexity: O(...)' and 'Space complexity: O(...)' strings in the solution HTML/text.
    Returns the *best* (usually optimal) complexities if clearly present.
    """
    if not solution_html:
        return None, None
    text = clean_html_to_text(solution_html)
    time_match = re.findall(
        r"Time\s*complexity:\s*O\(([^)]+)\)", text, flags=re.IGNORECASE
    )
    space_match = re.findall(
        r"Space\s*complexity:\s*O\(([^)]+)\)", text, flags=re.IGNORECASE
    )

    def score(comp: str) -> int:
        c = comp.replace(" ", "").lower()
        order = {
            "1": 0,
            "logn": 1,
            "n": 2,
            "nlogn": 3,
            "n^2": 4,
            "n2": 4,
            "n^3": 5,
        }
        c = c.replace("log(n)", "logn").replace("nlog(n)", "nlogn")
        return order.get(c, 99)

    def pick_best(matches: List[str]) -> Optional[str]:
        if not matches:
            return None
        normalized = [m.strip() for m in matches]
        best = min(normalized, key=score)
        return f"O({best})"

    time_c = pick_best(time_match)
    space_c = pick_best(space_match)
    return time_c, space_c


def split_description_parts(
    desc_text: str,
) -> Tuple[str, List[Dict[str, str]], List[str]]:
    """
    Split description text into exactly three parts:
    - description: main statement only
    - examples: extracted example dicts
    - constraints: extracted bullet list
    """
    # 1) Cut off "Constraints:" and everything after
    constraints_block = ""
    main_part = desc_text
    cons_match = re.search(r"Constraints:\s*(.*)", desc_text, re.DOTALL)
    if cons_match:
        constraints_block = cons_match.group(1)
        main_part = desc_text[: cons_match.start()].strip()

    # 2) Extract examples (and remove them from main_part)
    examples = []
    example_pattern = re.compile(
        r"(Example\s*\d*:.*?)(?=(?:Example\s*\d*:|Constraints:|$))",
        re.DOTALL | re.IGNORECASE,
    )
    for match in example_pattern.finditer(main_part):
        block = match.group(1).strip()
        # crude input/output parse
        input_line = re.search(r"Input:\s*(.*)", block)
        output_line = re.search(r"Output:\s*(.*)", block)
        explanation_line = re.search(r"Explanation:\s*(.*)", block)
        examples.append(
            {
                "input": input_line.group(1).strip() if input_line else "",
                "output": output_line.group(1).strip() if output_line else "",
                "explanation": explanation_line.group(1).strip()
                if explanation_line
                else "",
            }
        )
    # remove example text from description
    main_part = example_pattern.sub("", main_part).strip()

    # 3) Extract constraints lines
    constraints = []
    if constraints_block:
        constraints_block = re.split(
            r"Follow-up:", constraints_block, flags=re.IGNORECASE
        )[0]
        for line in constraints_block.splitlines():
            line = line.strip()
            if not line:
                continue
            # Remove leading bullet markers only; keep the rest as-is
            line = re.sub(r"^[\-\*\u2022]\s*", "", line)
            constraints.append(line)

    return main_part, examples, constraints


def normalize_one(raw: Dict[str, Any], overrides: Dict[str, Any], start_id: Optional[int] = None,) -> Dict[str, Any]:
    """
    Normalize a single problem record.
    
    Processes the raw problem data and optional overrides to produce a cleaned dictionary
    with normalized fields such as description, examples, constraints, stats, links, topics, and hints.
    """

    desc_html = raw.get("description", "")
    desc_text = clean_html_to_text(desc_html)

    description, examples, _ = split_description_parts(desc_text)
    constraints = extract_constraints_preserve_sup(desc_html)

    stats = parse_stats(raw.get("stats"), raw.get("acceptance_rate"))

    links = {
        "problem": raw.get("url"),
        "description": raw.get("description_url"),
        "solutions": raw.get("solution_url"),
    }

    topics = raw.get("topics", [])

    hints_raw = raw.get("hints")
    if isinstance(hints_raw, list):
        hints_list = hints_raw
    elif isinstance(hints_raw, str):
        hints_list = [hints_raw]
    else:
        hints_list = []

    cleaned = {
        "title": raw.get("title"),
        "slug": raw.get("titleSlug"),
        "difficulty": raw.get("difficulty"),
        "category": raw.get("category"),
        "topics": topics,
        "links": links,
        "stats": {
            "acceptance_rate": stats.get("acceptance_rate"),
            "submissions": stats.get("submissions"),
            "accepted": stats.get("accepted"),
            "likes": raw.get("likes"),
            "dislikes": raw.get("dislikes"),
        },
        "statement": {
            "description": description,
            "examples": examples,
            "constraints": constraints,
        },
        "hints": [clean_html_to_text(h or "") for h in hints_list],
    }

    provided_code = {
        "python": (raw.get("solution_code_python") or "").strip(),
        "java": (raw.get("solution_code_java") or "").strip(),
        "cpp": (raw.get("solution_code_cpp") or "").strip(),
    }
    any_code = any(bool(v) for v in provided_code.values())
    if any_code:
        cleaned["solutions"] = provided_code

    return cleaned


def normalize_file(
    input_path: str,
    output_path: str,
    first_n: int,
    start_id: int,
    overrides_path: Optional[str] = None,
) -> None:
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        if "problems" in data and isinstance(data["problems"], list):
            items = data["problems"]
        elif "items" in data and isinstance(data["items"], list):
            items = data["items"]
        else:
            items = [data]
    else:
        items = []

    overrides: Dict[str, Any] = {}
    if overrides_path:
        try:
            with open(overrides_path, "r", encoding="utf-8") as f:
                overrides = json.load(f)
        except Exception:
            overrides = {}

    if first_n is not None:
        items = items[:first_n]
    cleaned_all = []
    for i, item in enumerate(items):
        if item.get("difficulty") in ("Easy", "Medium"):
            cleaned = normalize_one(item, overrides)
            cleaned["id"] = str(start_id + i)
            cleaned_all.append(cleaned)
        else:
            pass

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_all, f, indent=2, ensure_ascii=False)


def main():
    # 🔧 configure your paths and options here
    input_file = "backend/scripts/leetcode_problems.json"
    output_file = "backend/scripts/cleaned.json"
    first_n = 1000   # set an int if you want to limit, e.g. 10
    overrides = None # or path to overrides.json
    start_id = 1

    normalize_file(input_file, output_file, first_n, start_id, overrides)


if __name__ == "__main__":
    main()