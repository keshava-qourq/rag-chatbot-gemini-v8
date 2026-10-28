"""The backing services this application is configured to reach.

Each entry maps a service to the environment variable that addresses it. Postgres
and Redis come from docker-compose.yml through .env.example for local dev; S3 is
real AWS in every environment, including the sandbox, so it is checked by the
variable the platform injects rather than a compose service.
"""

import os

SERVICES = {
    "postgres": "DATABASE_URL",
    "redis-queue": "REDIS_URL",
    "s3": "S3_BUCKET",
}


def configured_services() -> dict[str, bool]:
    """Each service mapped to whether its connection variable is set."""
    return {name: bool(os.getenv(var)) for name, var in SERVICES.items()}
