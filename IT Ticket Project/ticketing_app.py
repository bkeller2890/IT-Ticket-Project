from flask import Flask
from config import SECRET_KEY
from routes.tickets import bp as tickets_bp
from database import close_db
import os


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    app.register_blueprint(tickets_bp)
    app.teardown_appcontext(close_db)

    return app


if __name__ == "__main__":
    app = create_app()
    # Enable debug only when FLASK_DEBUG is set to '1' (default for local dev)
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug)
