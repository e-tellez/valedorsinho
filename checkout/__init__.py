import os

from flask import Flask, render_template

# config must be imported first – it loads .env and applies the SSL fix
# before the Adyen client (initialised inside config) makes any requests.
from checkout.config import FLASK_SECRET_KEY
from checkout.pages import bp as pages_bp
from checkout.advanced_api import bp as api_bp
from checkout.sessions_api import bp as sessions_api_bp
from homepage.pages import bp as homepage_bp
from setup.pages import bp as setup_bp
from payload_validator.pages import bp as validator_pages_bp
from payload_validator.api import bp as validator_api_bp
from payload_suggested.pages import bp as suggested_bp
from nfc_formatter.pages import bp as nfc_bp
from terminal_fleet.pages import bp as terminal_fleet_bp
from terminal_fleet.api import bp as terminal_fleet_api_bp
from terminal_payments.pages import bp as terminal_payments_bp


def create_app() -> Flask:
    """Application factory.

    Creates and configures the Flask app, pointing it at the project-level
    templates/ and static/ directories which live one level above this package.
    """
    # __file__ is checkout/__init__.py; going up one level gives the project root
    project_root = os.path.dirname(os.path.dirname(__file__))

    app = Flask(
        __name__,
        # Keep templates/ and static/ at the project root so they are easy to
        # find and are not buried inside the Python package directory.
        template_folder=os.path.join(project_root, "templates"),
        static_folder=os.path.join(project_root, "static"),
    )

    # Secret key required by Flask to sign the session cookie
    app.secret_key = FLASK_SECRET_KEY

    # Register blueprints – pages serve HTML, api handles JSON + redirects
    app.register_blueprint(homepage_bp)
    app.register_blueprint(setup_bp)
    app.register_blueprint(validator_pages_bp)
    app.register_blueprint(validator_api_bp)
    app.register_blueprint(suggested_bp)
    app.register_blueprint(nfc_bp)
    app.register_blueprint(terminal_payments_bp)
    app.register_blueprint(terminal_fleet_bp)
    app.register_blueprint(terminal_fleet_api_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(sessions_api_bp)

    @app.errorhandler(404)
    def page_not_found(e) -> tuple[str, int]:
        return render_template("errors/404.html"), 404

    return app
