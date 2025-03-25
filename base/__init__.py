from flask import Flask
from flask_mysqldb import MySQL
from config import Config

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    mysql.init_app(app)
    
    from com.controller import auth_controller, service_controller, admin_controller
    app.register_blueprint(auth_controller.bp)
    app.register_blueprint(service_controller.bp)
    app.register_blueprint(admin_controller.bp)
    
    return app 