from flask import Flask
from flasgger import Swagger
from config import Config
from routes.users import users_bp
from routes.events import events_bp
from routes.chats import chats_bp
from routes.health import health_bp
from database.db import init_db
from routes.s3_upload import s3_upload_bp


app = Flask(__name__)
app.config.from_object(Config)
swagger = Swagger(app)

app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(events_bp, url_prefix='/events')
app.register_blueprint(chats_bp, url_prefix='/chats')
app.register_blueprint(health_bp, url_prefix='/health')
app.register_blueprint(s3_upload_bp, url_prefix='/v1/s3')

if __name__ == '__main__':
    init_db()  
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)

