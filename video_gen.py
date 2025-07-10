import os
import time
import json
import requests


# Kie AI API constants
KIE_API_MODEL = "veo3_fast" # or "veo3"


def start_video_generation(prompt: str):
    """
    Submit the prompt to Kie AI's VEO3 model.
    Returns the task ID for tracking the generation job.
    """
    try:
        # Prepare the payload for VEO3
        payload = {
            "prompt": prompt,
            "model": KIE_API_MODEL
        }
            
        # Convert payload to JSON
        payload_json = json.dumps(payload)
        
        # Set up headers with API token
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {os.getenv("KIE_API_TOKEN")}'
        }
        
        # Make the API request
        url = f"https://api.kie.ai/api/v1/veo/generate"
        response = requests.post(url, headers=headers, data=payload_json)
        
        # Extract task ID from the response
        if response.status_code == 200:
            data = response.json()
            if "taskId" in data.get("data", {}):
                task_id = data["data"]["taskId"]
                print(f"Successfully submitted to Kie AI. Task ID: {task_id}")
                return task_id
        
        print(f"Error submitting to Kie AI: {response.text}")
        return None
    
    except Exception as e:
        print(f"Error submitting to Kie AI: {str(e)}")
        return None


def get_video_status(task_id: str):
    """
    Check the status of a video generation job using Kie AI API.
    """
    try:
        # Set up headers with API token
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {os.getenv("KIE_API_TOKEN")}'
        }
        
        # Make the API request
        url = f"https://api.kie.ai/api/v1/veo/record-info?taskId={task_id}"
        response = requests.get(url, headers=headers)
        
        # Process the response
        if response.status_code == 200:
            data = response.json()
            
            # Extract status information
            if "data" in data:
                result_data = data["data"]
                success_flag = result_data.get("successFlag")
                
                # Map Kie AI status codes to standard format
                if success_flag == 0:
                    return {"status": "in_progress", "task_id": task_id}
                elif success_flag == 1:
                    return {
                        "status": "completed",
                        "task_id": task_id,
                        "response": result_data.get("response", {})
                    }
                elif success_flag in [2, 3]:
                    error_msg = result_data.get("errorMessage", "Unknown error")
                    return {
                        "status": "failed",
                        "task_id": task_id,
                        "error": error_msg
                    }
            
            # If we can't determine the status, return the raw data
            return {"status": "unknown", "raw_data": data}
        else:
            return {"status": "error", "error": f"API error: {response.status_code}", "details": response.text}
    
    except Exception as e:
        print(f"Error checking Kie AI status: {str(e)}")
        return {"error": str(e), "status": "failed"}


def wait_for_completion(task_id: str, timeout_minutes: int = 10):
    """
    Wait for the video generation to complete using Kie AI API
    """
    print(f"Waiting for Kie AI video generation to complete (timeout: {timeout_minutes} minutes)...")
    
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    while True:
        # Check if we've exceeded the timeout
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            print(f"Timeout reached after {elapsed:.1f} seconds")
            return {"error": "Timeout reached", "status": "timeout"}
        
        # Get the current status
        result = get_video_status(task_id)
        status = result.get("status", "").lower()
        
        # If completed or error, return the result
        if status == "completed":
            print(f"Kie AI video generation completed successfully")
            return result
        elif status == "failed":
            print(f"Kie AI video generation failed: {result.get('error')}")
            return result
        
        # Wait before checking again (adjust as needed)
        time.sleep(30)