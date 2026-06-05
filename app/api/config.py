"""Application configuration and Adyen client initialization."""

import os

import Adyen


def _load_env_file(*candidates: str) -> None:
    """Parse a .env-style file and populate os.environ.

    Tries each path in *candidates* in order and loads the first one found.
    Lines starting with '#' are comments; blank lines are ignored.
    Values wrapped in single or double quotes have the quotes stripped.
    Already-set environment variables are NOT overwritten (same behaviour
    as python-dotenv's load_dotenv with override=False).
    """
    for path in candidates:
        if not os.path.isfile(path):
            continue
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                # Skip comments and blank lines
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                # Strip surrounding quotes from the value
                if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                    value = value[1:-1]
                # Do not override a value that was already set in the environment
                if key and key not in os.environ:
                    os.environ[key] = value
        break  # Stop after the first file that exists


# Resolve the project root (repo root directory)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Load .env if present, fall back to .env.example
_load_env_file(
    os.path.join(_PROJECT_ROOT, ".env"),
    os.path.join(_PROJECT_ROOT, ".env.example"),
)

# ---------------------------------------------------------------------------
# SSL certificate fix for macOS + Python 3 (framework builds)
# ---------------------------------------------------------------------------
if not os.environ.get("SSL_CERT_FILE"):
    try:
        import certifi
        os.environ["SSL_CERT_FILE"] = certifi.where()
    except ImportError:
        pass  # certifi not installed; user must set SSL_CERT_FILE manually

# ---------------------------------------------------------------------------
# Adyen client
# ---------------------------------------------------------------------------

adyen_client = Adyen.Adyen(
    xapikey=os.getenv("ADYEN_API_KEY"),
    platform=os.getenv("ADYEN_ENVIRONMENT", "test"),  # "test" or "live"
    merchant_account=os.getenv("ADYEN_MERCHANT_ACCOUNT"),
)

# ---------------------------------------------------------------------------
# Application constants read from environment
# ---------------------------------------------------------------------------

MERCHANT_ACCOUNT: str = os.getenv("ADYEN_MERCHANT_ACCOUNT", "")
CLIENT_KEY: str = os.getenv("ADYEN_CLIENT_KEY", "")
ADYEN_ENVIRONMENT: str = os.getenv("ADYEN_ENVIRONMENT", "test")
ADYEN_API_KEY: str = os.getenv("ADYEN_API_KEY", "")
CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# ---------------------------------------------------------------------------
# Supabase configuration
# ---------------------------------------------------------------------------

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
