import requests
import sys

# Configuration
API_URL = "http://localhost:8000/api/generate"

def generate_elevation(image_path):
    print(f"Uploading {image_path} to {API_URL}...")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            # Note: The server might take a while (30s+) to respond because it waits for NanoBanana
            response = requests.post(API_URL, files=files, timeout=300)
            
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print("\n✅ Success!")
                print(f"Task ID: {data['task_id']}")
                print(f"Result Image URL: {data['result_image_url']}")
            else:
                print(f"\n❌ Failed: {data}")
        else:
            print(f"\n❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python example_client.py <path_to_floor_plan_image>")
        # Create a dummy file for testing if user just runs it? No, better to instruct.
    else:
        generate_elevation(sys.argv[1])
