from flask import Blueprint, request, jsonify
import boto3  # type: ignore
from botocore.exceptions import ClientError
from botocore.client import Config as BotoConfig
import os
import uuid
from config import Config

s3_tools_bp = Blueprint("s3_tools", __name__)

S3_BUCKET = Config.S3_BUCKET
S3_REGION = Config.S3_REGION

# Create a Boto3 client for S3
s3_client = boto3.client(
    "s3", region_name=Config.S3_REGION, config=BotoConfig(signature_version="s3v4")
)


def get_presigned_url(object_key, expiration=600):  # Using 600 sec (10 min) for testing
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": Config.S3_BUCKET, "Key": object_key},
        ExpiresIn=expiration,
    )


@s3_tools_bp.route("/presigned-url", methods=["POST"])
def generate_presigned_url():
    data = request.get_json()
    file_type = data.get("file_type")
    file_name = data.get("file_name", "")

    # Whitelist allowed file types
    allowed_types = ["image/jpeg", "image/heic", "image/png"]
    if file_type not in allowed_types:
        return (
            jsonify(
                {
                    "error": "Invalid file type. Only image/jpeg image/heic image/png are allowed."
                }
            ),
            400,
        )

    # Generate a unique file key and store it under the "events/" folder
    file_extension = file_name.split(".")[-1] if "." in file_name else ""
    unique_key = (
        f"events/{uuid.uuid4()}.{file_extension}"
        if file_extension
        else f"events/{uuid.uuid4()}"
    )

    try:
        response = s3_client.generate_presigned_post(
            Bucket=S3_BUCKET,
            Key=unique_key,
            Fields={"Content-Type": file_type},
            Conditions=[{"Content-Type": file_type}],
            ExpiresIn=3600,  # URL valid for 1 hour
        )
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"data": response, "file_key": unique_key}), 200


@s3_tools_bp.route("/presigned-get-url", methods=["POST"])
def generate_presigned_get_url():
    """
    Generate a presigned URL for image upload.
    ---
    tags:
      - S3 Tools
    parameters:
      - in: body
        name: payload
        schema:
          type: object
          required:
            - file_type
          properties:
            file_name:
              type: string
            file_type:
              type: string
    responses:
      200:
        description: A presigned URL and file key.
      400:
        description: Invalid input.
      500:
        description: Server error.
    """
    data = request.get_json()
    file_key = data.get("file_key")
    if not file_key:
        return jsonify({"error": "file_key is required"}), 400

    try:
        get_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": file_key},
            ExpiresIn=3600,  # URL valid for 1 hour
        )
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"get_url": get_url}), 200


@s3_tools_bp.route("/delete", methods=["DELETE"])
def delete_file():
    data = request.get_json()
    file_key = data.get("file_key")
    if not file_key:
        return jsonify({"error": "file_key is required"}), 400

    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=file_key)
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "File deleted successfully"}), 200
