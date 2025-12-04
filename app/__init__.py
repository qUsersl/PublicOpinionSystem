from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import models to ensure they are known to Flask-Migrate
    from app import models

    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User
        return User.query.get(int(user_id))

    from .views.auth import auth_bp
    from .views.dashboard import dashboard_bp
    from .views.business import business_bp
    from .views.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(business_bp)
    app.register_blueprint(admin_bp)
    
    @app.context_processor
    def inject_settings():
        from .models.user import SystemSetting
        app_name_setting = SystemSetting.query.filter_by(key='app_name').first()
        logo_url_setting = SystemSetting.query.filter_by(key='logo_url').first()
        
        return {
            'app_name': app_name_setting.value if app_name_setting else 'POS',
            'logo_url': logo_url_setting.value if logo_url_setting else '',
            'current_user': current_user
        }

    return app
