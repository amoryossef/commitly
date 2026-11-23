"""commitly v0.1 - send staged changes to a model and print one commit message."""

import subprocess
import sys

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = "You write git commit messages. Reply with the message only."


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


def generate_message(diff: str) -> str:
    client = OpenAI()  # reads OPENAI_API_KEY from the environment
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": diff},
        ],
    )
    return response.choices[0].message.content.strip()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    load_dotenv()

    diff = get_staged_diff()
    if not diff.strip():
        print("Nothing staged — run git add first")
        return

    print(generate_message(diff))


if __name__ == "__main__":
    main()
