from flask import Flask
from flasgger import Swagger
from config import Config
from routes.users import users_bp
from routes.events import events_bp
from routes.chats import chats_bp
from database.db import init_db

app = Flask(__name__)
app.config.from_object(Config)
swagger = Swagger(app)

app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(events_bp, url_prefix='/events')
app.register_blueprint(chats_bp, url_prefix='/chats')

if __name__ == '__main__':
    init_db()  
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)

