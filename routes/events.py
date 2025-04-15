from flask import Blueprint, request, jsonify
import psycopg2
import json
from datetime import datetime
from database.db import get_db_connection
from os import getenv

import traceback

events_bp = Blueprint("events", __name__)


@events_bp.route("", methods=["POST"])
def create_event():
    data = request.get_json()
    required_fields = [
        "name",
        "address",
        "latitude",
        "longitude",
        "description",
        "image_sources",
        "event_date",
        "event_start_time",
        "event_end_time",
        "event_created",
        "event_type",
    ]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    image_sources = data.get("image_sources")
    image_sources_json = json.dumps(image_sources)

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO events (user_id, name, event_type, address, description, image_sources, latitude, longitude, event_date, event_start_time, event_end_time, event_created)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING event_id
            """,
            (
                data.get("user_id", 1),
                data["name"],
                data.get("event_type", "Any"),
                data["address"],
                data["description"],
                image_sources_json,
                data["latitude"],
                data["longitude"],
                data["event_date"],
                data["event_start_time"],
                data["event_end_time"],
                data["event_created"],
            ),
        )
        event_id = cur.fetchone()[0]
        conn.commit()
        return (
            jsonify(
                {
                    "event_id": event_id,
                    "user_id": data.get("user_id", 1),
                    "name": data["name"],
                    "event_type": data.get("event_type", "Any"),
                    "address": data["address"],
                    "description": data["description"],
                    "image_sources": image_sources,
                    "latitude": data["latitude"],
                    "longitude": data["longitude"],
                    "event_date": data["event_date"],
                    "event_start_time": data["event_start_time"],
                    "event_end_time": data["event_end_time"],
                    "event_created": data["event_created"],
                }
            ),
            201,
        )
    except Exception as e:
        conn.rollback()
        print("Error in create_event:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()
