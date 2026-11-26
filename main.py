import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config")

from django.core.management import execute_from_command_line
from app.config import HTTP_PORT

if __name__ == "__main__":
    execute_from_command_line([sys.argv[0], "runserver", f"127.0.0.1:{HTTP_PORT}"])
