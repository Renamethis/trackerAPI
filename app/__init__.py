from flask import Flask
from .API.Server import Server
#from .database.database import db_session
from flask_sqlalchemy import SQLAlchemy
from config import config
db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.add_url_rule('/server/', view_func=Server.as_view("server"))
    db.init_app(app)
    #app.run(host='0.0.0.0')
    return app