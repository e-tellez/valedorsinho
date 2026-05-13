import os

from flask import Flask, render_template

# config must be imported first – it loads .env and applies the SSL fix
# before the Adyen client (initialised inside config) makes any requests.
from checkout.config import FLASK_SECRET_KEY
from checkout.routes import bp


def create_app():
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

    # Register all checkout routes (pages + API endpoints)
    app.register_blueprint(bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    return app
