import os

import Adyen


def _load_env_file(*candidates):
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


# Resolve the project root (one level above this package directory)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# Load .env if present, fall back to .env.example (useful during development
# when the developer filled in .env.example directly instead of copying it)
_load_env_file(
    os.path.join(_PROJECT_ROOT, ".env"),
    os.path.join(_PROJECT_ROOT, ".env.example"),
)

# ---------------------------------------------------------------------------
# SSL certificate fix for macOS + Python 3 (framework builds)
# ---------------------------------------------------------------------------
# On macOS the Python.org installer does not link against the system keychain.
# urllib (used by the Adyen SDK) will raise SSLCertVerificationError unless we
# point it at a valid CA bundle.  If certifi is installed we use its bundle;
# SSL_CERT_FILE is honoured by both urllib and the ssl module.
if not os.environ.get("SSL_CERT_FILE"):
    try:
        import certifi
        os.environ["SSL_CERT_FILE"] = certifi.where()
    except ImportError:
        pass  # certifi not installed; user must set SSL_CERT_FILE manually

# ---------------------------------------------------------------------------
# Adyen client
# ---------------------------------------------------------------------------

# Initialise the Adyen Python library with credentials from environment variables.
# All kwargs are forwarded to AdyenClient, which is shared across every service
# (checkout, payment, recurring, etc.) exposed on the Adyen instance.
adyen_client = Adyen.Adyen(
    xapikey=os.getenv("ADYEN_API_KEY"),
    platform=os.getenv("ADYEN_ENVIRONMENT", "test"),  # "test" or "live"
    merchant_account=os.getenv("ADYEN_MERCHANT_ACCOUNT"),
)

# ---------------------------------------------------------------------------
# Application constants read from environment
# ---------------------------------------------------------------------------

# Merchant account name used in every Adyen API request body
MERCHANT_ACCOUNT = os.getenv("ADYEN_MERCHANT_ACCOUNT")

# Client key sent to the browser so the Adyen Web Component can communicate
# with Adyen's frontend services (tokenisation, 3DS iframe, etc.)
CLIENT_KEY = os.getenv("ADYEN_CLIENT_KEY")

# "test" or "live" – consumed by the Adyen Web Component in the browser
ADYEN_ENVIRONMENT = os.getenv("ADYEN_ENVIRONMENT", "test")

# Secret key used by Flask to sign the session cookie
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-me-in-production")
