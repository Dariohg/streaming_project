import os
from flask import Flask
from flask_login import LoginManager
from app.database.db import init_db
from app.database.models import User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    from app.database.models import User
    return User.get_by_id(int(user_id))


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_change_in_production'),
        DATABASE=os.path.join(app.instance_path, 'streaming.sqlite'),
        UPLOAD_FOLDER=os.path.join(app.static_folder, 'videos'),
        MAX_CONTENT_LENGTH=1024 * 1024 * 1024,  # 1GB max upload size
        ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'webm'},  # Añade esta línea
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.join(app.static_folder, 'hls'), exist_ok=True)  # Para segmentos HLS
    except OSError:
        pass

    init_db(app)

    login_manager.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.video import video_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(video_bp)

    from app.utils.helpers import format_duration
    app.jinja_env.filters['format_duration'] = format_duration

    return app