from app.config.settings import load_settings
from manage import run


if __name__ == "__main__":
    settings = load_settings()
    bind = (
        f"[{settings.http_host}]" if ":" in settings.http_host else settings.http_host
    )
    run(["runserver", f"{bind}:{settings.http_port}"])
