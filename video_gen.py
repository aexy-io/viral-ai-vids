import time
import fal_client


# fal.ai model identifier, using VEO3 model
FALAI_MODEL = "fal-ai/veo3"


def start_video_generation(prompt: str):
    """
    Submit the prompt to fal.ai's V3 model using the official client.
    Returns a handler with request ID for tracking the generation job.
    """
    try:
        # Prepare the arguments for VEO3
        arguments = {
            "prompt": prompt,
            "aspect_ratio": "16:9",  # Can be "16:9", "9:16", or "1:1"
            "duration": "8s",
            "enhance_prompt": True,
            "generate_audio": True
        }
        
        # Submit the request using fal-client
        handler = fal_client.submit(
            FALAI_MODEL,
            arguments=arguments
        )
        
        result = {"request_id": handler.request_id, "status": "submitted"}
        print(f"Successfully submitted to FAL. Request ID: {result['request_id']}")
        return result
    
    except Exception as e:
        print(f"Error submitting to FAL: {str(e)}")
        return {"error": str(e), "status": "failed"}


def get_video_status(request_id: str):
    """
    Check the status of a V3 video generation job using the official client.
    """
    try:
        # Get the status with logs included
        status_info = fal_client.status(FALAI_MODEL, request_id, with_logs=True)
        
        # Create a standardized response based on the status type
        if isinstance(status_info, fal_client.Completed):
            return {"status": "completed"}
        elif isinstance(status_info, fal_client.InProgress):
            # Format logs nicely if available
            logs = []
            if hasattr(status_info, 'logs') and status_info.logs:
                logs = [log.get('message', '') for log in status_info.logs]
            return {"status": "in_progress", "logs": logs}
        elif isinstance(status_info, fal_client.Queued):
            return {"status": "queued"}
    
    except Exception as e:
        print(f"Error checking FAL status: {str(e)}")
        return {"error": str(e), "status": "failed"}


def wait_for_v3_completion(request_id: str, timeout_minutes: int = 10):
    """
    Wait for the V3 video generation to complete using the fal-client.
    """
    print(f"Waiting for FAL video generation to complete (timeout: {timeout_minutes} minutes)...")
    
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    while True:
        # Check if we've exceeded the timeout
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            print(f"Timeout reached after {elapsed:.1f} seconds")
            return {"error": "Timeout reached", "status": "timeout"}
        
        # Get the current status
        result = get_video_status(request_id)
        status = result.get("status", "").lower()
        
        # If completed or error, return the result
        if status == "completed":
            # Get the final result with video URL
            final_result = get_video_result(request_id)
            return final_result
        elif status == "failed":
            print(f"FAL video generation failed: {result.get('error')}")
            return result
        
        # Wait before checking again (adjust as needed)
        time.sleep(30)


def get_video_result(request_id: str):
    """
    Get the final result with the generated video URL.
    """
    try:
        # Get the final result using fal-client
        result = fal_client.result(FALAI_MODEL, request_id)
        
        return {
            "status": "completed",
            "video_url": result["video"]["url"]
        }
    
    except Exception as e:
        print(f"Error getting video result: {str(e)}")
        return {"error": str(e), "status": "failed"}