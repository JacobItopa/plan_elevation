from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import shutil
import os
import uuid
from typing import Optional
from pydantic import BaseModel
import asyncio
from nanobanana import NanoBananaAPI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize App
app = FastAPI(title="NanoBanana Plan Elevation API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# API Key
API_KEY = os.getenv("NANOBANANA_API_KEY")
if not API_KEY:
    print("WARNING: NANOBANANA_API_KEY not found in environment variables.")

nano_api = NanoBananaAPI(API_KEY)

# Data Models
class GenerateRequest(BaseModel):
    prompt: str = "I want you to show the elevations of this plan"
    image_url: str

class GenerateResponse(BaseModel):
    task_id: str
    status: str
    result_url: Optional[str] = None

# Routes
@app.post("/api/generate")
async def generate_elevation(file: UploadFile = File(...), request: Request = None):
    try:
        # 1. Save the uploaded file locally
        file_extension = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Construct the URL for the image
        # CRITICAL: This needs to be a public URL for NanoBanana to access it.
        # If running locally without a tunnel, this will fail.
        # We try to determine the base URL from the request, but localhost won't work for external APIs.
        base_url = str(request.base_url)
        
        # Checking for ngrok/public URL in headers or env, otherwise warning
        # For this implementation, we assume the user has a way to expose it or we are just building the logic.
        # If the user is on localhost, we can try to use a service or just pass the localhost URL and let it fail with a clear message.
        
        image_url = f"{base_url}uploads/{filename}"
        
        # print for debugging
        print(f"Generated Image URL: {image_url}")
        
        if "localhost" in image_url or "127.0.0.1" in image_url:
            print("WARNING: Localhost detected. Attempting to upload to temporary public host (0x0.st) for API access...")
            try:
                with open(file_path, 'rb') as f:
                    response = requests.post('https://0x0.st', files={'file': f})
                    if response.ok:
                        image_url = response.text.strip()
                        print(f"Temporary public URL created: {image_url}")
                    else:
                        print(f"Failed to create temp URL: {response.text}")
                        # Fallback to localhost URL and let it fail if must
            except Exception as e:
                print(f"Error uploading to temp host: {e}")

        # 3. Call NanoBanana API
        # The prompt is fixed as per requirement: "I want you to show the elevations of this plan"
        prompt = "I want you to show the elevations of this plan"
        
        # We need to run the blocking API call in a thread
        try:
            task_id = await asyncio.to_thread(
                nano_api.generate_image, 
                prompt=prompt, 
                imageUrls=[image_url] # NanoBanana expects a list
            )
        except Exception as e:
             raise HTTPException(status_code=500, detail=f"NanoBanana API Error: {str(e)}")

        # 4. Wait for completion (Blocking for simplicity as per user example, but wrapped in thread)
        # In a real production app, we would return the task ID and have the client poll.
        # However, to match the user's "example" flow which waits, we will wait here.
        try:
            result = await asyncio.to_thread(nano_api.wait_for_completion, task_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Timeout or Error waiting for result: {str(e)}")
            
        return {
            "status": "success",
            "task_id": task_id,
            "result_image_url": result.get("resultImageUrl", ""),
            "original_result": result
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

@app.get("/api/download")
async def download_image(task_id: str):
    if not task_id:
        raise HTTPException(status_code=400, detail="Missing task_id")
    
    try:
        # Fetch status to get the URL
        # We run this in a thread because requests is blocking
        status = await asyncio.to_thread(nano_api.get_task_status, task_id)
        
        # Robustly extract URL
        data = status.get('data', status)
        url = data.get('resultImageUrl')
        
        if not url:
             raise HTTPException(status_code=404, detail="Image URL not found for this task (maybe expired or failed)")

        # Stream the file from the external URL
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Could not fetch image from source")
        
        def iterfile():
            yield from response.iter_content(chunk_size=4096)
            
        # Guess filename from URL or default
        filename = url.split("/")[-1]
        if "." not in filename:
            filename = f"elevation_{task_id}.jpg"
            
        return StreamingResponse(iterfile(), media_type=response.headers.get("content-type", "image/jpeg"), headers={"Content-Disposition": f"attachment; filename={filename}"})
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

# Mount static files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
