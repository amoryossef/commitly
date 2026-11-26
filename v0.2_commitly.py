"""commitly v0.2 - ask the model for a JSON commit description and build the message from it."""

import json
import subprocess
import sys

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "gpt-4o-mini"
ALLOWED_TYPES = ("feat", "fix", "refactor", "docs", "test", "chore", "perf")
MAX_SUBJECT_LENGTH = 72

SYSTEM_PROMPT = f"""You write git commit messages for a staged diff.
Reply with a single JSON object only, with exactly these keys:
- "type": the kind of change.
- "scope": the part of the project that changed (short, lowercase, e.g. "cart").
- "subject": one short line describing the change.
- "body": a list of 1-4 short strings with details about the change.
- "breaking": true if the change breaks existing code, otherwise false.

Rules:
- "type" must be one of: {", ".join(ALLOWED_TYPES)}.
- "subject" must be in English and start with a verb in the present tense ("add", not "added").
- "subject" may be at most {MAX_SUBJECT_LENGTH} characters and must not end with a period.

Example:
{{"type": "feat", "scope": "cart", "subject": "add coupon codes to checkout", "body": ["Validate coupon codes before applying the discount"], "breaking": false}}"""


def get_staged_diff() -> str:
    result = subprocess.run(
        ["git", "diff", "--staged"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(result.returncode)
    return result.stdout


def generate_commit_data(diff: str) -> dict:
    client = OpenAI()  # reads OPENAI_API_KEY from the environment
    response = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": diff},
        ],
    )
    return json.loads(response.choices[0].message.content)


def build_message(data: dict) -> str:
    header = data["type"]
    if data.get("scope"):
        header += f"({data['scope']})"
    if data.get("breaking"):
        header += "!"
    header += f": {data['subject']}"

    lines = [header]
    body = data.get("body") or []
    if body:
        lines.append("")
        lines.extend(f"- {item}" for item in body)
    return "\n".join(lines)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    load_dotenv()

    diff = get_staged_diff()
    if not diff.strip():
        print("Nothing staged — run git add first")
        return

    data = generate_commit_data(diff)
    print(build_message(data))


if __name__ == "__main__":
    main()
