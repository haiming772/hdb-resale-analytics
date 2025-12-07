# application/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Global extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=False)

    # Load config.cfg sitting in the same folder
    cfg_path = os.path.join(os.path.dirname(__file__), "config.cfg")
    app.config.from_pyfile(cfg_path)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Import models so SQLAlchemy knows them
    from .models import User  # noqa: F401

    # Register blueprints
    from .routes import main_bp
    from .auth import auth_bp
    from .errors import init_error_handlers

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # Register error handlers (no circular import)
    init_error_handlers(app)

    # Create tables
    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    return app
