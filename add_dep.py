"""Install a package and record it in requirements.txt automatically.

Usage:  python add_dep.py <package> [<package> ...]
"""

import re
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

REQUIREMENTS = Path(__file__).with_name("requirements.txt")


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def main() -> None:
    packages = sys.argv[1:]
    if not packages:
        sys.exit("Usage: python add_dep.py <package> [<package> ...]")

    subprocess.run([sys.executable, "-m", "pip", "install", *packages], check=True)

    lines = REQUIREMENTS.read_text(encoding="utf-8").splitlines() if REQUIREMENTS.exists() else []
    for pkg in packages:
        name = re.split(r"[<>=!~\[ ]", pkg, maxsplit=1)[0]
        entry = f"{name}=={version(name)}"
        lines = [l for l in lines if normalize(re.split(r"[<>=!~\[ ]", l, maxsplit=1)[0]) != normalize(name)]
        lines.append(entry)
        print(f"Recorded {entry} in requirements.txt")

    lines = sorted((l for l in lines if l.strip()), key=str.lower)
    REQUIREMENTS.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
