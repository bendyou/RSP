import os
from pathlib import Path
import re
from secrets import token_urlsafe

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]


def initialize_env(root: Path = ROOT) -> bool:
    env_file = root / ".env"
    if env_file.exists():
        values = dotenv_values(env_file, interpolate=False)
        if (values.get("DJANGO_SECRET_KEY") or "").strip():
            return False
        original = env_file.read_text()
        replacement = f"DJANGO_SECRET_KEY={token_urlsafe(48)}"
        lines = original.splitlines()
        found = False
        for index, line in enumerate(lines):
            if re.match(r"^\s*(?:export\s+)?DJANGO_SECRET_KEY(?:\s*=.*)?\s*$", line):
                lines[index] = replacement
                found = True
        if not found:
            lines.append(replacement)
        env_file.write_text("\n".join(lines) + "\n")
        env_file.chmod(0o600)
        return True
    template = (root / ".env.example").read_text()
    lines = template.splitlines()
    if sum(line.startswith("DJANGO_SECRET_KEY=") for line in lines) != 1:
        raise ValueError("В .env.example нужна одна строка DJANGO_SECRET_KEY=")
    content = (
        "\n".join(
            f"DJANGO_SECRET_KEY={token_urlsafe(48)}"
            if line.startswith("DJANGO_SECRET_KEY=")
            else line
            for line in lines
        )
        + "\n"
    )
    try:
        with open(
            env_file, "x", opener=lambda path, flags: os.open(path, flags, 0o600)
        ) as stream:
            stream.write(content)
    except FileExistsError:
        return False
    return True


if __name__ == "__main__":
    if initialize_env():
        print(
            "Локальный .env подготовлен; отсутствующий секрет сгенерирован, файл исключён из Git"
        )
    else:
        print("Локальный .env уже существует и оставлен без изменений")
