from flask import Blueprint, request, jsonify
import boto3 # type: ignore
from botocore.exceptions import ClientError
import os
import uuid

s3_tools_bp = Blueprint('s3_tools', __name__)

# Use environment variables for bucket and region
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_REGION = os.environ.get("S3_REGION")

# Create a Boto3 client for S3
s3_client = boto3.client('s3', region_name=S3_REGION)

@s3_tools_bp.route('/presigned-url', methods=['POST'])
def generate_presigned_url():
    """
    Expects a JSON payload with:
      - file_name: original file name (optional)
      - file_type: MIME type of the file (e.g., "image/jpeg" or "image/heic")
    Returns a pre-signed URL for uploading to S3 and a unique file key.
    """
    data = request.get_json()
    file_type = data.get('file_type')
    file_name = data.get('file_name', '')
    
    # Whitelist allowed file types
    allowed_types = ["image/jpeg", "image/heic"]
    if file_type not in allowed_types:
        return jsonify({'error': 'Invalid file type. Only image/jpeg and image/heic are allowed.'}), 400

    # Generate a unique file key and store it under the "events/" folder
    file_extension = file_name.split('.')[-1] if '.' in file_name else ''
    unique_key = f"events/{uuid.uuid4()}.{file_extension}" if file_extension else f"events/{uuid.uuid4()}"
    
    try:
        response = s3_client.generate_presigned_post(
            Bucket=S3_BUCKET,
            Key=unique_key,
            Fields={"Content-Type": file_type},
            Conditions=[{"Content-Type": file_type}],
            ExpiresIn=3600  # URL valid for 1 hour
        )
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'data': response, 'file_key': unique_key}), 200

@s3_tools_bp.route('/delete', methods=['DELETE'])
def delete_file():
    """
    Expects a JSON payload with:
      - file_key: the key of the file to delete from S3.
    Returns a confirmation message if deletion is successful.
    """
    data = request.get_json()
    file_key = data.get('file_key')
    if not file_key:
        return jsonify({'error': 'file_key is required'}), 400

    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=file_key)
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'File deleted successfully'}), 200