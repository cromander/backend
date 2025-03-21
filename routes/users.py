from flask import Blueprint, request, jsonify
import psycopg2
from os import getenv

users_bp = Blueprint('users', __name__)

def get_db_connection():
    return psycopg2.connect(
        host=getenv("DB_HOST"),
        database=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD")
    )

@users_bp.route('', methods=['POST'])
def create_user():
    """
    Create a new user
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - username
          properties:
            username:
              type: string
    responses:
      201:
        description: User created successfully
        schema:
          type: object
          properties:
            user_id:
              type: integer
            username:
              type: string
      400:
        description: Username required or already exists
    """
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({'error': 'Username required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING user_id", (data['username'],))
        user_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({'user_id': user_id, 'username': data['username']}), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'Username already exists'}), 400
    finally:
        cur.close()
        conn.close()
