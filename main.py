import os
import uuid
from typing import Optional
from pathlib import Path

import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="S3 Image Upload Service", version="1.0.0")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
print(AWS_SECRET_ACCESS_KEY)
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_BASE_URL = os.getenv("S3_BASE_URL")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}


def is_valid_image(filename: str) -> bool:
    """Check if the file has a valid image extension."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def upload_to_s3(file_content: bytes, s3_key: str, content_type: str) -> str:
    """Upload file to S3 and return the public URL."""
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType=content_type,
            # ACL 제거 - 버킷 정책으로 공개 접근 설정
        )

        # Return the public URL
        return f"{S3_BASE_URL}/{s3_key}"

    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not found")
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")


@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    """Display the upload form."""
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload", response_class=HTMLResponse)
async def upload_image(
    request: Request,
    prefix: str = Form(..., description="S3 prefix/folder path"),
    file: UploadFile = File(..., description="Image file to upload"),
):
    """Handle image upload to S3."""

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    if not is_valid_image(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read file content
    try:
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    # Generate unique filename
    file_extension = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Clean prefix (remove leading/trailing slashes)
    clean_prefix = prefix.strip().strip("/")

    # Create S3 key
    if clean_prefix:
        s3_key = f"{clean_prefix}/{unique_filename}"
    else:
        s3_key = unique_filename

    # Upload to S3
    try:
        file_url = upload_to_s3(file_content, s3_key, file.content_type or "image/jpeg")

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "success": True,
                "file_url": file_url,
                "original_filename": file.filename,
                "s3_key": s3_key,
                "file_size": len(file_content),
            },
        )

    except HTTPException as e:
        return templates.TemplateResponse(
            "result.html", {"request": request, "success": False, "error": e.detail}
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "S3 Upload Service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8888)
