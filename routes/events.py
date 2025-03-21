from flask import Blueprint, request, jsonify
import psycopg2
import json
from services.geocode import geocode_address
from os import getenv

events_bp = Blueprint('events', __name__)

def get_db_connection():
    return psycopg2.connect(
        host=getenv("DB_HOST"),
        database=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD")
    )

@events_bp.route('', methods=['POST'])
def create_event():
    """
    Create a new event
    ---
    tags:
      - Events
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - user_id
            - address
            - description
          properties:
            user_id:
              type: integer
            address:
              type: string
            description:
              type: string
            image_sources:
              type: array
              items:
                type: string
    responses:
      201:
        description: Event created successfully
      400:
        description: Missing required fields or geocoding error
      500:
        description: Server error
    """
    data = request.get_json()
    if not data or not all(key in data for key in ['user_id', 'address', 'description']):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        latitude, longitude = geocode_address(data['address'])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    image_sources = data.get('image_sources', [])
    image_sources_json = json.dumps(image_sources)

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            '''
            INSERT INTO events (user_id, address, latitude, longitude, description, image_sources)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING event_id
            ''',
            (data['user_id'], data['address'], latitude, longitude, data['description'], image_sources_json)
        )
        event_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({
            'event_id': event_id,
            'user_id': data['user_id'],
            'address': data['address'],
            'latitude': latitude,
            'longitude': longitude,
            'description': data['description'],
            'image_sources': image_sources
        }), 201
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
