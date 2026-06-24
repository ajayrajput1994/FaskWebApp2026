# app/__init__.py
from flask import Flask
from .extensions import db, login_manager, mail, migrate
from .config import config_map, DevelopmentConfig
from app.model import User
from app.models.profile import Profile  
from app.models.post import Post  
from app.models.comment import Comment  
from app.models.tag import Tag, post_tags

def create_app(config_name='development'):
    """
    Application factory. Call this to create a Flask app instance.
    Pass 'testing' or 'production' to get different configs.
    """
    app = Flask(__name__)

    # 1. Load config
    cfg = config_map.get(config_name, DevelopmentConfig)
    app.config.from_object(cfg)

    # 2. Initialise extensions — NOW they get bound to this app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # 3. Register blueprints — each gets its URL prefix
    from .auth import auth_bp
    from .dashboard import dashboard_bp
    from .api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(api_bp,       url_prefix='/api/v1')

    # 4. Register error handlers
    from flask import render_template
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    # 4. Create DB tables if they don't exist (development only)
    with app.app_context(): 
        db.create_all()

    return app  # ← returns a fully assembled app