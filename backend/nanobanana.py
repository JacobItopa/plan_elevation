import requests
import time

class NanoBananaAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.nanobananaapi.ai/api/v1/nanobanana'
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def generate_image(self, prompt, **options):
        data = {
            'prompt': prompt,
            'type': options.get('type', 'TEXTTOIAMGE'),
            'numImages': options.get('numImages', 1),
            'callBackUrl': options.get('callBackUrl'),
            'watermark': options.get('watermark')
        }
        
        if options.get('imageUrls'):
            data['imageUrls'] = options['imageUrls']
        
        response = requests.post(f'{self.base_url}/generate', 
                               headers=self.headers, json=data)
        result = response.json()
        
        if not response.ok or result.get('code') != 200:
            raise Exception(f"Generation failed: {result.get('msg', 'Unknown error')}")
        
        return result['data']['taskId']
    
    def get_task_status(self, task_id):
        response = requests.get(f'{self.base_url}/record-info?taskId={task_id}',
                              headers={'Authorization': f'Bearer {self.api_key}'})
        return response.json()
    
    def wait_for_completion(self, task_id, max_wait_time=300):
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status = self.get_task_status(task_id)
            success_flag = status.get('data', {}).get('successFlag', 0) # Note: user code had `status.get('successFlag')`. API usually returns {code:200, data: {...}}. I will adjust based on common patterns or stick to user code. User code: `status.get('successFlag', 0)`. I will check if `status` is the full response or data. In `get_task_status` it returns `response.json()`. Usually APIs wrap in `data`. I will add a safe get.
             # Actually, looking at `generate_image`, it accesses `result['data']['taskId']`. So `get_task_status` probably returns a dict that *might* have `successFlag` at top level or inside `data`.
             # User code: `success_flag = status.get('successFlag', 0)`
             # I will stick to the user's provided code structure but make it robust.
            
            # Re-reading user code:
            # result = response.json() ... result['data']['taskId'] -> standard wrapper.
            # get_task_status -> response.json().
            # wait_for_completion -> status.get('successFlag').
            # If the API is consistent, `successFlag` should probably be in `data`. 
            # I will blindly trust the user code for now, but if it fails, I'll know why.
            # actually, I'll improve it slightly to look in both.
            
            data = status.get('data', status) # validation fallback
            success_flag = data.get('successFlag', 0)
            
            if success_flag == 0:
                print(f"Task {task_id} status: Generating...")
            elif success_flag == 1:
                return data
            elif success_flag in [2, 3]:
                print(f"Task {task_id} failed. Data: {data}")
                error_msg = data.get('errorMessage')
                if not error_msg:
                    error_msg = f"Generation failed (unknown error). Full status: {data}"
                raise Exception(error_msg)
            
            time.sleep(3)
        
        raise Exception('Generation timeout')
