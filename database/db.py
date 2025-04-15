import os
import psycopg2
from config import Config


def get_db_connection():
    return psycopg2.connect(
        host=Config.DB_HOST,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
    )


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE
        );
    """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            event_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            event_type TEXT NOT NULL DEFAULT 'Any',
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            description TEXT NOT NULL,
            image_sources JSONB,
            event_date TIMESTAMP NOT NULL,
            event_start_time TIMESTAMP NOT NULL,
            event_end_time TIMESTAMP NOT NULL,
            event_created TIMESTAMP NOT NULL
        );
    """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            message_id SERIAL PRIMARY KEY,
            event_id INT NOT NULL,
            user_id INT NOT NULL,
            message TEXT NOT NULL,
            timestamp BIGINT NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
    """
    )
    conn.commit()
    cur.close()
    conn.close()
