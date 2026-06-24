# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
migrate = Migrate()

# Created here, but NOT yet connected to any Flask app.
# They get connected inside create_app() via .init_app(app)
db = SQLAlchemy()
mail = Mail()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'   # redirect if @login_required fails
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'
