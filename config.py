from dataclasses import dataclass
import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> None:
        return None


@dataclass
class AppConfig:
    deepseek_api_key: str
    deepseek_base_url: str
    deepseek_model: str
    sec_user_agent: str
    request_timeout: int


def load_config() -> AppConfig:
    load_dotenv()

    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()
    deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
    sec_user_agent = os.getenv(
        "SEC_USER_AGENT", "DemoMVP/1.0 (contact: your_email@example.com)"
    ).strip()

    timeout_str = os.getenv("REQUEST_TIMEOUT", "30").strip()
    try:
        request_timeout = int(timeout_str)
    except ValueError:
        request_timeout = 30

    return AppConfig(
        deepseek_api_key=deepseek_api_key,
        deepseek_base_url=deepseek_base_url,
        deepseek_model=deepseek_model,
        sec_user_agent=sec_user_agent,
        request_timeout=request_timeout,
    )
