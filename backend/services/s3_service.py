import boto3
from flask import current_app

def get_s3_client():
    return boto3.client(
        's3',
        region_name=current_app.config['S3_REGION'],
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY']
    )

def upload_file_to_s3(file, filename):
    s3_client = get_s3_client()
    try:
        s3_client.upload_fileobj(file, current_app.config['S3_BUCKET'], filename)
    except Exception as e:
        print(f"S3 upload error: {e}")
        raise

def delete_file_from_s3(filename):
    s3_client = get_s3_client()
    try:
        s3_client.delete_object(Bucket=current_app.config['S3_BUCKET'], Key=filename)
    except Exception as e:
        print(f"S3 delete error: {e}")
        raise

