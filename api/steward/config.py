"""steward-api configuration: the docs/02 §11 environment variables for steward-api.

Read once per call (cheap) so tests can monkeypatch the environment. Secrets are only ever
read here and passed to the client that needs them; they are never logged.
"""

import os
from dataclasses import dataclass
from pathlib import Path


def _env(name: str, default: str = "") -> str:
    value = os.environ.get(name, "")
    return value if value.strip() else default


@dataclass(frozen=True)
class Settings:
    nebius_api_key: str
    token_factory_base_url: str
    model_primary: str
    model_fallback: str
    model_fallback_2: str
    reasoning_effort: str
    tavily_api_key: str
    mail_mode: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    demo_mail_redirect: str
    owner_email: str
    steward_proxy_key: str
    steward_mcp_token: str
    hermes_api_url: str
    hermes_api_key: str
    db_path: Path
    hermes_data_dir: Path
    workspace_dir: Path
    steward_demo: bool
    steward_dev: bool
    daily_request_cap: int

    @property
    def memories_dir(self) -> Path:
        return self.hermes_data_dir / "memories"


def get_settings() -> Settings:
    port = _env("SMTP_PORT", "0")
    cap = _env("DAILY_REQUEST_CAP", "0")
    return Settings(
        nebius_api_key=_env("NEBIUS_API_KEY"),
        token_factory_base_url=_env(
            "TOKEN_FACTORY_BASE_URL", "https://api.tokenfactory.nebius.com/v1"
        ).rstrip("/"),
        model_primary=_env("MODEL_PRIMARY", "nvidia/Nemotron-3_5-Lightning"),
        model_fallback=_env("MODEL_FALLBACK", "nvidia/nemotron-3-super-120b-a12b"),
        model_fallback_2=_env("MODEL_FALLBACK_2", "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"),
        reasoning_effort=_env("REASONING_EFFORT", "low"),
        tavily_api_key=_env("TAVILY_API_KEY"),
        mail_mode=_env("MAIL_MODE", "demo"),
        smtp_host=_env("SMTP_HOST"),
        smtp_port=int(port) if port.isdigit() else 0,
        smtp_user=_env("SMTP_USER"),
        smtp_password=_env("SMTP_PASSWORD"),
        demo_mail_redirect=_env("DEMO_MAIL_REDIRECT"),
        owner_email=_env("OWNER_EMAIL", "maya@rao-consulting.example"),
        steward_proxy_key=_env("STEWARD_PROXY_KEY"),
        steward_mcp_token=_env("STEWARD_MCP_TOKEN"),
        hermes_api_url=_env("HERMES_API_URL", "http://hermes:8642").rstrip("/"),
        hermes_api_key=_env("HERMES_API_KEY"),
        db_path=Path(_env("STEWARD_DB_PATH", "/data/steward.db")),
        hermes_data_dir=Path(_env("HERMES_DATA_DIR", "/hermes-data")),
        workspace_dir=Path(_env("WORKSPACE_DIR", "/workspace")),
        steward_demo=_env("STEWARD_DEMO", "0") == "1",
        steward_dev=_env("STEWARD_DEV", "0") == "1",
        daily_request_cap=int(cap) if cap.isdigit() else 0,
    )
