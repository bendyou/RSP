from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
checked = 0
for file in ROOT.rglob("*.md"):
    if any(
        part.startswith(".") or part in {"venv", "node_modules"}
        for part in file.relative_to(ROOT).parts
    ):
        continue
    for raw in re.findall(r"\]\(([^)]+)\)", file.read_text()):
        target = raw.split("#", 1)[0].split(' "', 1)[0].strip("<>")
        if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            continue
        assert (file.parent / unquote(target)).exists(), (
            f"Сломанная ссылка: {file.relative_to(ROOT)} → {target}"
        )
        checked += 1
print(f"OK: {checked} локальных ссылок Markdown")
