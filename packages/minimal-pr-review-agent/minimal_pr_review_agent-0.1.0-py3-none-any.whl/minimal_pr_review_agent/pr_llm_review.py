#!/usr/bin/env python3
import os
import sys
import json
import textwrap
import httpx

from typing import List, Dict, Any
from github import Github
from github.PullRequest import PullRequest
from pydantic import ValidationError
from llm_pr_review_agent.pr_components import ReviewInputs, CodeReviewItem, CodeReviewOutput, FilePatch, ReviewCategory
from llm_pr_review_agent.llm_request.request_gemini import request_gemini, GeminiModels 

DEFAULT_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
MAX_RESPONSE_TOKENS = int(os.getenv("MAX_RESPONSE_TOKENS", "2000"))
REVIEW_CONTEXT_BYTES = int(os.getenv("REVIEW_CONTEXT_BYTES", "120000"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_github_pr() -> PullRequest:
    repo_full_name = os.getenv("GITHUB_REPOSITORY")
    pr_number_str = os.getenv("PR_NUMBER")

    if not repo_full_name:
        # Local run: scripts/pr_llm_review.py <repo_full_name> <pr_number>
        if len(sys.argv) < 3:
            print("Usage (local): scripts/pr_llm_review.py <repo_full_name> <pr_number>")
            sys.exit(2)
        repo_full_name = sys.argv[1]
        pr_number_str = sys.argv[2]

    if not GITHUB_TOKEN:
        print("Missing GITHUB_TOKEN in env.")
        sys.exit(2)

    gh = Github(GITHUB_TOKEN)
    repo = gh.get_repo(repo_full_name)

    if pr_number_str is None:
        event_path = os.getenv("GITHUB_EVENT_PATH")
        if event_path and os.path.exists(event_path):
            with open(event_path, "r", encoding="utf-8") as f:
                event = json.load(f)
            pr_number = event.get("number") or event.get("pull_request", {}).get("number")
        else:
            print("Could not determine PR number.")
            sys.exit(2)
    else:
        pr_number = int(pr_number_str)

    return repo.get_pull(pr_number)


def collect_pr_context(pr: PullRequest) -> ReviewInputs:
    files: List[FilePatch] = []
    total_bytes = 0

    for f in pr.get_files():
        patch = f.patch if hasattr(f, "patch") else None
        patch_bytes = len(patch.encode("utf-8", errors="ignore")) if patch else 0
        if patch and patch_bytes + total_bytes > REVIEW_CONTEXT_BYTES:
            head = patch[: int(REVIEW_CONTEXT_BYTES / 2)]
            tail = patch[-int(REVIEW_CONTEXT_BYTES / 2) :]
            patch = head + "\n... [truncated] ...\n" + tail
            patch_bytes = len(patch.encode("utf-8", errors="ignore"))
        total_bytes += patch_bytes

        files.append(
            FilePatch(
                filename=f.filename,
                status=f.status,
                patch=patch,
                additions=f.additions,
                deletions=f.deletions,
                changes=f.changes,
            )
        )

    title = pr.title or ""
    body = pr.body or ""
    return ReviewInputs(
        repo=pr.base.repo.full_name,
        pr_number=pr.number,
        title=title,
        body=body,
        head=pr.head.ref,
        base=pr.base.ref,
        author=pr.user.login if pr.user else "unknown",
        files=files,
    )


def build_review_prompt(inputs: ReviewInputs) -> str:
    file_summaries = []
    for f in inputs.files:
        header = f"File: {f.filename} | status: {f.status} | +{f.additions} -{f.deletions} (Δ {f.changes})"
        patch_block = f.patch or "(no patch available)"
        file_summaries.append(header + "\n" + "```diff\n" + patch_block + "\n```")

    files_section = "\n\n".join(file_summaries) if file_summaries else "(No file changes detected)"

    schema = textwrap.dedent(
        """
        Output STRICT JSON (double quotes, no comments, no trailing commas) matching exactly this schema:
        {
          "code_review": [
            {
              "file": "relative/path/from/repo/root.ext",
              "lines": [line] or [start_line, end_line],
              "category": "bug" | "syntax_error" | "documentation" | "style" | "edge_case" | "performance" | "typo",
              "comment": "short explanation of the issue and its impact",
              "suggestion": "optional concrete suggestion or code snippet"
            }
          ]
        }
        """
    ).strip()

    guidelines = textwrap.dedent(
        f"""
        You are a senior software engineer acting as a strict code reviewer.
        Review the pull request diffs and produce structured feedback.
        Focus categories: documentation, style consistency, edge cases, accidental issues (typos/syntax), performance, and bugs.
        Rules:
        - Only include files that changed in this PR.
        - Use line numbers from the new (head) version of the file.
        - Keep comments concise and actionable.
        - Prefer concrete suggestions.
        - If no issues, return an empty list: {{"code_review": []}}.
        {schema}
        """
    ).strip()

    pr_header = (
        f"PR #{inputs.pr_number} - {inputs.title}\n"
        f"Author: {inputs.author}\n"
        f"Base: {inputs.base} ← Head: {inputs.head}\n\n"
        f"Description:\n{inputs.body}\n\n"
        f"Diffs:\n{files_section}"
    )

    return guidelines + "\n\n" + pr_header


async def call_llm_for_json(prompt: str) -> CodeReviewOutput:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is required")
    items = json.loads(request_gemini(GeminiModels.GEMINI_2_5_PRO, prompt).text)
    return CodeReviewOutput(code_review=items)


def group_review_comments_for_github(items: List[CodeReviewItem]) -> List[Dict[str, Any]]:
    comments: List[Dict[str, Any]] = []
    for item in items:
        if not item.lines:
            continue
        body_lines = [f"[{item.category}] {item.comment}"]
        if item.suggestion:
            body_lines.append("")
            body_lines.append("Suggestion (apply via GitHub review):")
            body_lines.append("```suggestion")
            body_lines.append(item.suggestion)
            body_lines.append("```")
        body = "\n".join(body_lines)

        # Multi-line vs single line comment payload (line-based API)
        if len(item.lines) == 1:
            comments.append(
                {
                    "path": item.file,
                    "side": "RIGHT",
                    "line": int(item.lines[0]),
                    "body": body,
                }
            )
        elif len(item.lines) >= 2:
            start_line = int(min(item.lines[0], item.lines[1]))
            end_line = int(max(item.lines[0], item.lines[1]))
            comments.append(
                {
                    "path": item.file,
                    "side": "RIGHT",
                    "line": end_line,
                    "start_line": start_line,
                    "start_side": "RIGHT",
                    "body": body,
                }
            )
    return comments


def filter_items_to_changed_files(items: List[CodeReviewItem], changed_files: List[str]) -> List[CodeReviewItem]:
    changed = set(changed_files)
    return [it for it in items if it.file in changed]


def submit_chunked_review(pr: PullRequest, comments: List[Dict[str, Any]], header: str) -> None:
    # GitHub may limit number of comments in a single review; chunk to be safe
    CHUNK = 20
    if not comments:
        pr.create_issue_comment(header + "No line-anchored comments were generated.")
        return

    for i in range(0, len(comments), CHUNK):
        chunk = comments[i : i + CHUNK]
        pr.create_review(body=header if i == 0 else None, event="COMMENT", comments=chunk)


def main() -> None:
    pr = get_github_pr()
    inputs = collect_pr_context(pr)
    prompt = build_review_prompt(inputs)

    import asyncio

    llm_output = asyncio.run(call_llm_for_json(prompt))

    changed_files = [f.filename for f in pr.get_files()]
    items = filter_items_to_changed_files(llm_output.code_review, changed_files)

    comments = group_review_comments_for_github(items)

    header = f"Automated LLM Review for PR #{inputs.pr_number}\n"

    if comments:
        try:
            submit_chunked_review(pr, comments, header)
            return
        except Exception as e:
            # Fallback to issue comment if line-anchored review fails
            pass

    # Fallback: post a single issue comment with the JSON
    pretty = json.dumps(llm_output.model_dump(), indent=2)
    pr.create_issue_comment(header + "\n```json\n" + pretty + "\n```")


if __name__ == "__main__":
    main() 
