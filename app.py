from fastapi import FastAPI, File, UploadFile
from pdf2image import convert_from_bytes
from fastapi.responses import JSONResponse
import boto3
from io import BytesIO
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

app = FastAPI()

# Initialize S3 client
s3 = boto3.client(
    's3',
    endpoint_url=f"https://{os.getenv('SPACE_REGION')}.digitaloceanspaces.com",
    aws_access_key_id=os.getenv('SPACES_KEY'),
    aws_secret_access_key=os.getenv('SPACES_SECRET'),
    region_name=os.getenv('SPACE_REGION')
)

@app.get("/")
async def root():
    return {"message": "PDF to Image converter is running"}

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        return JSONResponse(
            status_code=400,
            content={'error': 'File must be PDF'}
        )

    try:
        contents = await file.read()
        images = convert_from_bytes(contents)
        
        img_byte_arr = BytesIO()
        images[0].save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        file_name = f'converted_{file.filename}.png'
        
        # Upload to Spaces
        s3.upload_fileobj(
            img_byte_arr, 
            os.getenv('SPACE_NAME'),
            file_name,
            ExtraArgs={'ACL': 'public-read'}
        )
        
        url = f"https://{os.getenv('SPACE_NAME')}.{os.getenv('SPACE_REGION')}.digitaloceanspaces.com/{file_name}"
        return JSONResponse(content={'url': url})
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'error': str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)