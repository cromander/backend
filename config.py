import os

# for local development, you can uncomment the following lines
# from dotenv import load_dotenv

# Load environment variables from .env file
# load_dotenv()


class Config:
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DEBUG = os.getenv("DEBUG") == "True"
    S3_BUCKET = os.environ.get("S3_BUCKET")
    S3_REGION = os.environ.get("S3_REGION")
