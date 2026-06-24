# app/__init__.py
from flask import Flask
from .extensions import db, login_manager, mail, migrate
from .config import config_map, DevelopmentConfig
from app.model import User
from app.models.profile import Profile  
from app.models.post import Post  
from app.models.comment import Comment  
from app.models.tag import Tag, post_tags
from flask_wtf.csrf import generate_csrf


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


    from flask import render_template
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    from datetime import datetime
    
    @app.context_processor
    def inject_globals():
        return {'now': datetime.utcnow()}

    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    @app.template_filter('time_ago')
    def time_ago_filter(dt):
        """Shows '3 minutes ago', '2 days ago', etc."""
        from datetime import datetime
        diff = datetime.utcnow() - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return f'{seconds} seconds ago'
        elif seconds < 3600:
            return f'{seconds // 60} minutes ago'
        elif seconds < 86400:
            return f'{seconds // 3600} hours ago'
        else:
            return f'{diff.days} days ago'
    
    # 4. Create DB tables if they don't exist 
    with app.app_context(): 
        db.create_all()

    return app  # ← returns a fully assembled app