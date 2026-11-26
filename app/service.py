from time import monotonic

started_at = monotonic()


def get_health(name, version, environment):
    return {
        "status": "pass",
        "app_name": name,
        "version": version,
        "environment": environment,
        "uptime_seconds": int(monotonic() - started_at),
    }
