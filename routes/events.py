from flask import Blueprint, request, jsonify
import psycopg2
import json
from datetime import datetime
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
            - name
            - address
            - description
            - event_date
          properties:
            name:
              type: string
            address:
              type: string
            description:
              type: string
            event_date:
              type: string
              format: date-time
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
    required_fields = ['name', 'address', 'description', 'event_date']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        latitude, longitude = geocode_address(data['address'])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    image_sources = data.get('image_sources', [])
    image_sources_json = json.dumps(image_sources)
    
    # Capture the current time for when the event is created.
    event_created = datetime.utcnow()

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            '''
            INSERT INTO events (name, address, latitude, longitude, description, image_sources, event_date, event_created)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING event_id
            ''',
            (data['name'], data['address'], latitude, longitude, data['description'], image_sources_json, data['event_date'], event_created)
        )
        event_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({
            'event_id': event_id,
            'name': data['name'],
            'address': data['address'],
            'latitude': latitude,
            'longitude': longitude,
            'description': data['description'],
            'image_sources': image_sources,
            'event_date': data['event_date'],
            'event_created': event_created.isoformat() + 'Z'
        }), 201
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
