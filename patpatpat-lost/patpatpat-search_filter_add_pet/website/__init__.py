from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
from .user import User
mysql = MySQL()



def create_app():
    mysql = MySQL()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'akndk djn anjanfn'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'pet_db'
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    mysql.init_app(app)
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    login_manager = LoginManager()
    login_manager.login_view = 'views.home'
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            return User(id=user[0], email=user[1], first_name=user[2], password=user[3])
        return None
    
    return app