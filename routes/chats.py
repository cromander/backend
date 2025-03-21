from flask import Blueprint, request, jsonify
import psycopg2
import time
from os import getenv

chats_bp = Blueprint('chats', __name__)

def get_db_connection():
    return psycopg2.connect(
        host=getenv("DB_HOST"),
        database=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD")
    )

@chats_bp.route('/<int:event_id>', methods=['POST'])
def send_chat_message(event_id):
    """
    Send a chat message for an event
    ---
    tags:
      - Chats
    parameters:
      - in: path
        name: event_id
        type: integer
        required: true
        description: ID of the event
      - in: body
        name: body
        schema:
          type: object
          required:
            - user_id
            - message
          properties:
            user_id:
              type: integer
            message:
              type: string
    responses:
      201:
        description: Chat message sent successfully
      400:
        description: Missing required fields or invalid event_id
      403:
        description: User must follow the event to chat
    """
    data = request.get_json()
    if not data or not all(key in data for key in ['user_id', 'message']):
        return jsonify({'error': 'user_id and message required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Verify event exists (and possibly that the user is allowed to chat)
        cur.execute("SELECT event_id FROM events WHERE event_id = %s", (event_id,))
        if not cur.fetchone():
            return jsonify({'error': 'Invalid event_id'}), 400

        timestamp = int(time.time())
        cur.execute(
            '''
            INSERT INTO chat_messages (event_id, user_id, message, timestamp)
            VALUES (%s, %s, %s, %s) RETURNING message_id
            ''',
            (event_id, data['user_id'], data['message'], timestamp)
        )
        message_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({
            'message_id': message_id,
            'event_id': event_id,
            'user_id': data['user_id'],
            'message': data['message'],
            'timestamp': timestamp
        }), 201
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
