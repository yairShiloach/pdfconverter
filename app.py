from fastapi import FastAPI, File, UploadFile
from pdf2image import convert_from_bytes
from fastapi.responses import JSONResponse
import boto3
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{os.getenv("SPACE_REGION")}.digitaloceanspaces.com",
    aws_access_key_id=os.getenv("SPACES_KEY"),
    aws_secret_access_key=os.getenv("SPACES_SECRET")
)

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        logger.debug("Converting PDF...")
        images = convert_from_bytes(contents)
        logger.debug("Conversion successful")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})
