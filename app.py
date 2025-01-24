from fastapi import FastAPI, File, UploadFile
from pdf2image import convert_from_bytes
from fastapi.responses import JSONResponse
import boto3
from io import BytesIO
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
s3 = boto3.client(
   "s3",
   endpoint_url=f"https://{os.getenv('SPACE_REGION')}.digitaloceanspaces.com",
   aws_access_key_id=os.getenv("SPACES_KEY"),
   aws_secret_access_key=os.getenv("SPACES_SECRET")
)

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
   if not file.filename.endswith('.pdf'):
       return JSONResponse(
           status_code=400,
           content={"error": "File must be PDF"}
       )

   try:
       logger.debug("Reading file contents...")
       contents = await file.read()
       
       logger.debug("Converting PDF to image...")
       images = convert_from_bytes(
           contents,
           poppler_path="/usr/bin"  # Add explicit poppler path
       )
       logger.debug(f"Converted {len(images)} pages")
       
       img_byte_arr = BytesIO()
       images[0].save(img_byte_arr, format='PNG')
       img_byte_arr.seek(0)
       
       # Upload to Spaces
       bucket_name = os.getenv('SPACE_NAME')
       file_name = f'converted_{file.filename}.png'
       
       s3.upload_fileobj(
           img_byte_arr, 
           bucket_name,
           file_name,
           ExtraArgs={'ACL': 'public-read'}
       )
       
       url = f'https://{bucket_name}.{os.getenv("SPACE_REGION")}.digitaloceanspaces.com/{file_name}'
       return JSONResponse(content={'url': url})
       
   except Exception as e:
       logger.error(f"Error: {str(e)}")
       import sys
       logger.error(f"Full error: {sys.exc_info()}")
       return JSONResponse(status_code=500, content={'error': str(e)})

@app.get("/")
async def root():
   return {"status": "PDF converter is running"}