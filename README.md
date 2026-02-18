# NanoBanana Plan to Elevation AI

A clear and modern web application that transforms 2D floor plans into stunning elevations using the NanoBanana API.

## Project Structure

- `backend/`: FastAPI server handling image uploads and API communication.
- `frontend/`: Beautiful glassmorphism UI for interacting with the tool.
- `example_client.py`: Python script for developers to test the API programmatically.

## Prerequisites

- Python 3.8+
- [Optional but Recommended] `ngrok` for exposing your local server (required for the external API to access your uploaded images during development).

## Setup & Run

1.  **Install Dependencies**:
    ```bash
    pip install fastapi uvicorn requests python-multipart python-dotenv
    ```

    Create a `.env` file in the `backend` directory with your API key:
    ```
    NANOBANANA_API_KEY=your_api_key_here
    ```

2.  **Start the Server**:
    Navigate to the `backend` directory and run:
    ```bash
    cd backend
    uvicorn main:app --reload
    ```
    The server will start at `http://localhost:8000`.

3.  **Access the Web App**:
    Open your browser and go to `http://localhost:8000`.

## Deployment on Render

This project is ready for Render deployment.

1.  Push the code to GitHub.
2.  Create a **Web Service** on Render.
3.  Set **Build Command**: `pip install -r requirements.txt`
4.  Set **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5.  **Important**: Add your `NANOBANANA_API_KEY` in the Environment Variables settings.

## ⚠️ Important Note for Local Development ⚠️

The NanoBanana API requires a **publicly accessible URL** for the input image.

 **Automatic Fallback**: The server includes a fallback mechanism. If it detects `localhost`, it attempts to upload the image to a temporary public host (`0x0.st`) so the API can access it.

 **Recommended**: For better control, use `ngrok`:
1.  Run `ngrok http 8000`
2.  Access the web app via the ngrok URL.

## Developer API Usage

You can integreate this into your own apps by calling the endpoint:

**Endpoint**: `POST /api/generate`
**Body**: `multipart/form-data` with a `file` field.

**Python Example**:
```bash
python example_client.py path/to/your/plan.jpg
```
