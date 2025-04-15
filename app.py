from flask import Flask, jsonify

# from flask_cors import CORS
from flasgger import Swagger
from config import Config

from routes.users import users_bp
from routes.events import events_bp
from routes.chats import chats_bp
from routes.health import health_bp
from routes.s3_tools import s3_tools_bp
from routes.graphql import graphql_bp as graphql_events_bp

from database.db import init_db, get_db_connection
import traceback

app = Flask(__name__)
# CORS(app)
app.config.from_object(Config)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: not rule.rule.startswith("/gql"),
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}
swagger = Swagger(
    app, config=swagger_config, template_file="config/swagger_template.yaml"
)

app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(events_bp, url_prefix="/events")
app.register_blueprint(chats_bp, url_prefix="/chats")
app.register_blueprint(graphql_events_bp, url_prefix="/gql")
app.register_blueprint(health_bp, url_prefix="/health")
app.register_blueprint(s3_tools_bp, url_prefix="/v1/s3")


@app.route("/", methods=["GET"])
def index():
    return "OK", 200


@app.route("/debug-spec", methods=["GET"])
def debug_spec():
    try:
        specs = swagger.get_apispecs()  # This returns a list
        return jsonify(specs[0])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/test-db", methods=["GET"])
def test_db():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "DB connection successful"}), 200
    except Exception as e:
        print("DB connection test failed:", traceback.format_exc())
        return jsonify({"error": "DB connection failed", "details": str(e)}), 500


@app.route("/test", methods=["POST"])
def test_endpoint():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=app.config["DEBUG"], host="0.0.0.0", port=5000)
