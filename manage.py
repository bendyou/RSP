import os
import sys

from django.core.management import execute_from_command_line


def run(arguments: list[str] | None = None) -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.django_settings")
    execute_from_command_line(
        sys.argv if arguments is None else [sys.argv[0], *arguments]
    )


if __name__ == "__main__":
    run()
