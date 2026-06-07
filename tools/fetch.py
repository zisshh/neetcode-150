#!/usr/bin/env python3
"""
Scaffold a NeetCode/LeetCode problem folder for local C++ practice.

Usage:
    ./new https://leetcode.com/problems/two-sum/
    ./new two-sum

Fetches problem data from LeetCode's public GraphQL API, then creates:
    NNNN-slug/README.md       scraped description, constraints, examples
    NNNN-slug/solution.cpp    empty signature stub (you solve this)
    NNNN-slug/tests.cpp       example cases wired as doctest TEST_CASEs

No login required for free problems. No AI, no hints, no solutions.
"""
import json
import re
import sys
import os
import html
import urllib.request

GRAPHQL = "https://leetcode.com/graphql"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

QUERY = """
query getQuestion($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    questionFrontendId
    title
    titleSlug
    difficulty
    content
    exampleTestcases
    sampleTestCase
    metaData
    topicTags { name }
    codeSnippets { langSlug code }
  }
}
"""


def slug_from_arg(arg: str) -> str:
    """Accept a full URL or a bare slug."""
    arg = arg.strip().rstrip("/")
    m = re.search(r"problems/([a-z0-9\-]+)", arg)
    if m:
        return m.group(1)
    return arg


def fetch(slug: str) -> dict:
    payload = json.dumps({"query": QUERY, "variables": {"titleSlug": slug}}).encode()
    req = urllib.request.Request(
        GRAPHQL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (practice-harness)",
            "Referer": f"https://leetcode.com/problems/{slug}/",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    q = data.get("data", {}).get("question")
    if not q:
        sys.exit(f"error: problem '{slug}' not found (check the slug/URL)")
    return q


# ---------------------------------------------------------------------------
# HTML -> readable markdown (light touch, no external deps)
# ---------------------------------------------------------------------------
def html_to_md(content: str) -> str:
    if not content:
        return ""
    s = content
    s = re.sub(r"(?is)<sup>(.*?)</sup>", r"^\1", s)
    s = re.sub(r"(?is)<sub>(.*?)</sub>", r"_\1", s)
    s = re.sub(r"(?is)<strong[^>]*>(.*?)</strong>", r"**\1**", s)
    s = re.sub(r"(?is)<b[^>]*>(.*?)</b>", r"**\1**", s)
    s = re.sub(r"(?is)<em[^>]*>(.*?)</em>", r"*\1*", s)
    s = re.sub(r"(?is)<code[^>]*>(.*?)</code>", r"`\1`", s)
    s = re.sub(r"(?is)<pre[^>]*>(.*?)</pre>", lambda m: "\n```\n" + strip_tags(m.group(1)).strip() + "\n```\n", s)
    s = re.sub(r"(?is)<li[^>]*>(.*?)</li>", r"- \1\n", s)
    s = re.sub(r"(?is)</?ul[^>]*>", "\n", s)
    s = re.sub(r"(?is)</?ol[^>]*>", "\n", s)
    s = re.sub(r"(?is)<br\s*/?>", "\n", s)
    s = re.sub(r"(?is)</p>", "\n\n", s)
    s = re.sub(r"(?is)<p[^>]*>", "", s)
    s = strip_tags(s)
    s = html.unescape(s)
    s = re.sub(r"(?m)^[ \t]+-\s+", "- ", s)   # de-indent bullets
    s = re.sub(r"(?m)^[ \t]+$", "", s)         # blank out whitespace-only lines
    s = re.sub(r"\n\s*\n(- )", r"\n\1", s)     # tighten gaps between bullets
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def strip_tags(s: str) -> str:
    return re.sub(r"(?is)<[^>]+>", "", s)


def cpp_snippet(q: dict) -> str:
    for sn in q.get("codeSnippets") or []:
        if sn.get("langSlug") == "cpp":
            return sn["code"]
    return "class Solution {\npublic:\n    // TODO: signature unavailable from API\n};"


def parse_method(snippet: str):
    """Extract (return_type, name, params) from the public method in the stub.

    Scans line by line so access labels (public:) and class lines never get
    mistaken for the signature, and the return type never spans a newline.
    """
    labels = ("public:", "private:", "protected:")
    for line in snippet.splitlines():
        ls = line.strip()
        if not ls or ls in labels or ls.startswith(("class ", "struct ", "//", "*", "/*")):
            continue
        m = re.match(r"([A-Za-z_][\w:<>,*&\s]*?)\s+([A-Za-z_]\w*)\s*\(([^)]*)\)", ls)
        if m:
            return m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    return None


def build_readme(q: dict) -> str:
    fid = q["questionFrontendId"]
    title = q["title"]
    diff = q["difficulty"]
    tags = ", ".join(t["name"] for t in q.get("topicTags") or [])
    url = f"https://leetcode.com/problems/{q['titleSlug']}/"
    body = html_to_md(q.get("content") or "")
    out = [f"# {fid}. {title}", ""]
    out.append(f"**Difficulty:** {diff}  ")
    if tags:
        out.append(f"**Topics:** {tags}  ")
    out.append(f"**Link:** {url}")
    out.append("")
    out.append("---")
    out.append("")
    out.append(body if body else "_(no description returned)_")

    # Raw example data + signature, kept here so you have it when writing tests.cpp.
    out.append("")
    out.append("---")
    out.append("")
    out.append("## For your tests")
    method = parse_method(cpp_snippet(q))
    if method:
        rtype, name, params = method
        out.append("")
        out.append("Signature you call:")
        out.append("")
        out.append("```cpp")
        out.append(f"{rtype} Solution::{name}({params})")
        out.append("```")
    raw = (q.get("exampleTestcases") or "").strip()
    if raw:
        out.append("")
        out.append("Raw example test cases (one value per line, grouped per example):")
        out.append("")
        out.append("```")
        out.append(raw)
        out.append("```")
    return "\n".join(out) + "\n"


def default_return_body(snippet: str) -> str:
    """Insert `return {};` into empty method bodies so an unsolved stub fails
    cleanly (wrong answer) instead of crashing with UB on a missing return.

    `{}` value-initializes any non-void return type (0, false, "", {}, nullptr),
    so it is a safe universal placeholder. void methods are left untouched.
    """
    def repl(m: re.Match) -> str:
        rtype = m.group("rtype").strip()
        head, body, tail = m.group("head"), m.group("body"), m.group("tail")
        if body.strip():
            return m.group(0)               # already has a body — leave it
        if rtype in ("void",) or rtype.endswith("void"):
            return m.group(0)               # void: nothing to return
        return f"{head}\n        return {{}};\n    {tail}"

    pat = re.compile(
        r"(?P<head>(?P<rtype>[A-Za-z_][\w:<>,*&\s]*?)\s+[A-Za-z_]\w*\s*\([^)]*\)\s*\{)"
        r"(?P<body>[^{}]*?)"
        r"(?P<tail>\})"
    )
    return pat.sub(repl, snippet)


def build_solution(q: dict, snippet: str) -> str:
    fid = q["questionFrontendId"]
    title = q["title"]
    snippet = default_return_body(snippet)
    return (
        f"// {fid}. {title}\n"
        f"// https://leetcode.com/problems/{q['titleSlug']}/\n"
        f"//\n"
        f"// Solve it yourself. Run:  ./run {folder_name(q)}\n\n"
        f"#pragma once\n"
        f"#include <algorithm>\n"
        f"#include <climits>\n"
        f"#include <cmath>\n"
        f"#include <functional>\n"
        f"#include <map>\n"
        f"#include <numeric>\n"
        f"#include <queue>\n"
        f"#include <set>\n"
        f"#include <stack>\n"
        f"#include <string>\n"
        f"#include <unordered_map>\n"
        f"#include <unordered_set>\n"
        f"#include <vector>\n"
        f"using namespace std;\n\n"
        f"{snippet}\n"
    )


def folder_name(q: dict) -> str:
    return f"{int(q['questionFrontendId']):04d}-{q['titleSlug']}"


def write(path: str, text: str):
    with open(path, "w") as f:
        f.write(text)


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: ./new <leetcode-url-or-slug>")
    slug = slug_from_arg(sys.argv[1])
    q = fetch(slug)
    folder = os.path.join(ROOT, folder_name(q))
    if os.path.exists(folder):
        sys.exit(f"exists already: {folder_name(q)}  (delete it to regenerate)")
    os.makedirs(folder)
    snippet = cpp_snippet(q)
    write(os.path.join(folder, "README.md"), build_readme(q))
    write(os.path.join(folder, "solution.cpp"), build_solution(q, snippet))
    print(f"created {folder_name(q)}/")
    print(f"  README.md      problem description + raw example test data")
    print(f"  solution.cpp   <- solve here")
    print(f"  (write tests.cpp yourself — see TESTING_GUIDE.md, then ./run {folder_name(q)})")


if __name__ == "__main__":
    main()
