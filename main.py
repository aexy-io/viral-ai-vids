import os
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel
from video_gen import start_video_generation, wait_for_v3_completion
from utils import log_to_excel, ainvoke_llm, get_current_date
from prompts import GENERATE_IDEAS_PROMPT, GENERATE_VIDEO_SCRIPT_PROMPT


# Models for structured outputs
class IdeaItem(BaseModel):
    Caption: str
    Idea: str
    Environment: str
    
class IdeasList(BaseModel):
    ideas: list[IdeaItem]

async def generate_video_ideas(topic: str, count: int = 1):
    """
    Generate a creative idea for video content based on the given topic.
    Similar to the Ideas AI Agent in N8N workflow.
    """
    print(f"Generating ideas for topic: '{topic}'...")
    user_message = f"Generate {count} creative video ideas about: {topic}"
    
    # Use the AI invocation function with structured output
    result = await ainvoke_llm(
        model="gpt-4.1-mini",
        system_prompt=GENERATE_IDEAS_PROMPT,
        user_message=user_message,
        response_format=IdeasList,
        temperature=0.7
    )
    return result.ideas


async def generate_veo3_video_prompt(idea: str, environment: str):
    """
    Generate a V3-compatible prompt based on the idea and environment.
    Similar to the Prompts AI Agent in N8N workflow.
    """
    print(f"Creating video prompt for idea: '{idea}'...")
    
    user_message = f"""
    Create a V3 prompt for this idea: {idea}
    Environment context: {environment}
    """
    
    # Use the AI invocation function
    result = await ainvoke_llm(
        model="gpt-4.1-mini",
        system_prompt=GENERATE_VIDEO_SCRIPT_PROMPT,
        user_message=user_message,
        temperature=0.7
    )
    return result


async def run_workflow(topic: str, count: int = 1):
    """
    Run the complete workflow from idea generation to video creation.
    """
    try:
        # Step 1: Generate idea
        ideas = await generate_video_ideas(topic, count)
        print(f"Generated ideas:\n\n{ideas}")
        
        # Process each idea sequentially for simplicity - can be upgraded to parallel processing for better efficiency later
        for idea in ideas:
            # Create a log entry for excel
            log_entry = {
                'idea': idea.Idea,
                'caption': idea.Caption,
                'environment': idea.Environment,
                'prompt': "",
                'status': "in_progress",
                'created_at': get_current_date(),
                'video_url': None
            }
        
            # Step 2: Generate V3 prompt
            prompt = await generate_veo3_video_prompt(idea.Idea, idea.Environment)
            log_entry['prompt'] = prompt
            
            # Log the initial entry and get the row index
            row_index = log_to_excel(log_entry)
            
            # Step 3: Submit to fal.ai 
            submission = start_video_generation(prompt)
            
            if not submission or isinstance(submission, dict) and "error" in submission:
                error_msg = submission.get("error", "Unknown error during submission") if isinstance(submission, dict) else "Failed to get request ID"
                log_entry['status'] = "failed"
                log_entry['error'] = error_msg
                # Update the existing row with error information
                log_to_excel(log_entry, row_index)
                return None
            
            request_id = submission
            log_entry['request_id'] = request_id
            
            # Update the log with request ID
            log_to_excel(log_entry, row_index)
            
            # Step 4: Wait for completion
            result = wait_for_v3_completion(request_id)
            
            # Step 5: Update status and log results
            if "error" in result:
                log_entry['status'] = "failed"
                log_entry['error'] = result['error']
            else:
                log_entry['status'] = "completed"
                video_url = result.get("video_url", "")
                if not video_url and "output" in result:
                    if isinstance(result["output"], dict) and "video_url" in result["output"]:
                        video_url = result["output"]["video_url"]
                        
                log_entry['video_url'] = video_url
                print(f"Video URL: {video_url}")
            
            # Step 6: Update the Excel log with final results
            log_to_excel(log_entry, row_index)
    except Exception as e:
        print(f"Error in workflow: {str(e)}")
        return None


async def main():
    # You can configure this to run on a schedule
    topic = "Alien comedian roasting humans for trusting AI"  # Example topic
    
    # Number of ideas/videos to generate
    count = 1
    
    # Run main function
    await run_workflow(topic, count)
    

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if FAL_KEY environment variable is set
    if not os.environ.get("FAL_KEY"):
        print("Warning: FAL_KEY environment variable not set")
    
    # Check if OPENROUTER_API_KEY environment variable is set
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("Warning: OPENROUTER_API_KEY environment variable not set")
    
    asyncio.run(main())