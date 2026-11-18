import os
from flask import Flask
from .extensions import db, login_manager, csrf, migrate


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-change-this-secret"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///blog.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        BLOG_TITLE="Inkflow",
    )
    if config_object:
        app.config.from_object(config_object)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    from .auth.routes import auth_bp
    from .main.routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app
