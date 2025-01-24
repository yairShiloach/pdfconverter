from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    return JSONResponse(content={"status": "received"})

@app.get("/")
async def root():
    return {"message": "working"}