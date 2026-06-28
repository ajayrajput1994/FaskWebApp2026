# app/__init__.py  ← REPLACE the full file

from flask import Flask, render_template, request, jsonify
from .extensions import db, login_manager, mail, talisman, migrate, limiter
from .config import config_map, DevelopmentConfig
from app.model import User
from app.models.profile import Profile  
from app.models.post import Post  
from app.models.comment import Comment  
from app.models.tag import Tag, post_tags
from app.models.Invoice import Invoice
from .logging_config import configure_logging  
import time


def create_app(config_name='development'):
    app = Flask(__name__)
    cfg = config_map.get(config_name, DevelopmentConfig)
    app.config.from_object(cfg)

    # ── Bind extensions ───────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # ── Rate limiter — bind with Redis URI from config ────────────
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    limiter.storage_uri = redis_url
    limiter.init_app(app)

    configure_logging(app)

    # ── Security headers via Talisman ─────────────────────────────
    # Content Security Policy — controls which sources browser trusts
    csp = {
        'default-src': "'self'",
        # Scripts: only from your own domain
        # 'script-src': ["'self'"],
        'script-src':  ["'self'", "'unsafe-inline'"],
        # Styles: your domain + Google Fonts
        # 'style-src':  ["'self'", 'fonts.googleapis.com'],
        'style-src':   ["'self'", "'unsafe-inline'"],
        # Fonts: your domain + Google Fonts CDN
        'font-src':   ["'self'", 'fonts.gstatic.com'],
        # Images: your domain + inline data: URIs (for avatars etc.)
        'img-src':    ["'self'", 'data:'],
        # Never allow <object>, <embed>, or <applet>
        'object-src': "'none'",
        # Prevent base tag hijacking
        'base-uri':   "'self'",
        # Forms can only POST to your own domain
        'form-action': "'self'",
    }

    # Permissions Policy — disable browser APIs you don't use
    permissions_policy = {
        'geolocation':  '()',   # nobody can request location
        'microphone':   '()',   # nobody can access microphone
        'camera':       '()',   # nobody can access camera
        'payment':      '()',   # no payment API
        'usb':          '()',   # no USB API
    }

    is_production = config_name == 'production'

    # app/__init__.py  ← FIND and REPLACE the entire talisman.init_app() block

    talisman.init_app(
        app,

        # ── HTTPS ─────────────────────────────────────────────────
        force_https=is_production,

        # ── HSTS ──────────────────────────────────────────────────
        strict_transport_security=is_production,
        strict_transport_security_max_age=31536000,
        strict_transport_security_include_subdomains=True,

        # ── Clickjacking ──────────────────────────────────────────
        frame_options='DENY',

        # ── Content Security Policy ───────────────────────────────
        content_security_policy=csp,
        # content_security_policy_nonce_in=['script-src'],

        # ── Referrer leakage ──────────────────────────────────────
        referrer_policy='strict-origin-when-cross-origin',
    )

    @app.after_request
    def add_security_headers(response):
        # X-Content-Type-Options — prevents MIME sniffing attacks
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # X-XSS-Protection — legacy browsers XSS filter
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Permissions-Policy — disables browser APIs you don't use
        response.headers['Permissions-Policy'] = permissions_policy
        return response
    
    # ── Register blueprints ───────────────────────────────────────
    from .auth import auth_bp
    from .dashboard import dashboard_bp
    from .api import api_bp
    from .organisations.routes import org_bp
    from .billing.routes import billing_bp

    app.register_blueprint(auth_bp,      url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(api_bp,       url_prefix='/api/v1')
    app.register_blueprint(org_bp)
    app.register_blueprint(billing_bp)

    # ── Cache-Control on all dashboard routes ─────────────────────
    @app.after_request
    def set_cache_headers(response):
        if request.endpoint and request.endpoint.startswith('dashboard.'):
            response.headers['Cache-Control'] = (
                'no-store, no-cache, must-revalidate, max-age=0'
            )
            response.headers['Pragma'] = 'no-cache'
        return response

    # ── Error handlers ────────────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        app.logger.error(
            'Unhandled exception on %s %s',
            request.method,
            request.path,
            exc_info=True,  # includes full Python traceback
        )
        return render_template('errors/500.html'), 500

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {'now': datetime.utcnow()}

    # ADD this new error handler for rate limit exceeded:
    @app.errorhandler(429)
    def too_many_requests(e):
        # API requests get JSON, browser requests get HTML
        if request.accept_mimetypes.accept_json:
            return jsonify(error='Too many requests. Please slow down.'), 429
        return render_template('errors/429.html'), 429

    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)

    # ── Custom template filter ────────────────────────────────────
    @app.template_filter('time_ago')
    def time_ago_filter(dt):
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
    
    @app.before_request
    def start_timer():
        request._start_time = time.time()

    @app.after_request
    def log_request(response):
        # Only log in production (not debug mode)
        if not app.debug:
            duration_ms = int((time.time() - request._start_time) * 1000)
            # Log every request at INFO level
            app.logger.info(
                '%s %s %s %dms',
                request.method,
                request.path,
                response.status_code,
                duration_ms,
            )
            if duration_ms > 500:
                app.logger.warning(
                    'SLOW_REQUEST %s %s took %dms',
                    request.method,
                    request.path,
                    duration_ms,
                )
        return response
    
    with app.app_context():
        db.create_all()

    return app
