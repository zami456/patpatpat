from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
from .user import User
mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'akndk djn anjanfn'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'pet_db'
    mysql.init_app(app)

    # Define the table creation SQL commands
    TABLES = {}
    TABLES['users'] = (
        "CREATE TABLE `users` ("
        "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
        "  `email` VARCHAR(255) NOT NULL UNIQUE,"
        "  `first_name` VARCHAR(255) NOT NULL,"
        "  `password` VARCHAR(255) NOT NULL,"
        "  `contact_no` VARCHAR(11) NOT NULL,"
        "  `facebook` VARCHAR(255),"
        "  `whatsapp` VARCHAR(255)"
        ") ENGINE=InnoDB")

    TABLES['pets'] = (
        "CREATE TABLE `pets` ("
        "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
        "  `name` VARCHAR(100) NOT NULL,"
        "  `city` VARCHAR(100) NOT NULL,"
        "  `area` VARCHAR(100) NOT NULL,"
        "  `pet_type` VARCHAR(100),"
        "  `breed` VARCHAR(100),"
        "  `age` INT NOT NULL,"
        "  `sex` VARCHAR(10),"
        "  `vaccinated` BOOLEAN,"
        "  `neutered` BOOLEAN,"
        "  `description` TEXT,"
        "  `image_filename` VARCHAR(255),"
        "  `user_id` INT,"
        "  `img2` VARCHAR(255),"
        "  `img3` VARCHAR(255),"
        "  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE"
        ") ENGINE=InnoDB")

    TABLES['adoption_request'] = (
        "CREATE TABLE `adoption_request` ("
        "  `user_id` INT NOT NULL,"
        "  `pet_id` INT NOT NULL,"
        "  PRIMARY KEY (`user_id`, `pet_id`),"
        "  `message` TEXT,"
        "  `date_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,"
        "  FOREIGN KEY (`pet_id`) REFERENCES `pets` (`id`) ON DELETE CASCADE"
        ") ENGINE=InnoDB")

    # Create tables
    with app.app_context():
        cursor = mysql.connection.cursor()
        for table_name in TABLES:
            table_description = TABLES[table_name]
            try:
                print(f"Creating table {table_name}: ", end='')
                cursor.execute(table_description)
                print("OK")
            except Exception as err:
                if "already exists" in str(err):
                    print(f"Table {table_name} already exists.")
                else:
                    print(err)
        cursor.close()

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