import os
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel
from video_gen import start_video_generation
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
        model="gemini-1.5-flash",
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
        model="gemini-1.5-pro",
        system_prompt=GENERATE_VIDEO_SCRIPT_PROMPT,
        user_message=user_message,
        temperature=0.7
    )
    return result


async def run_workflow(topic: str, count: int = 1):
    """
    Run the complete workflow from idea generation to storyboard creation.
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
                'video_url': "",
                'gemini_output': "",
                'error': ""
            }
        
            # Step 2: Generate V3 prompt
            prompt = await generate_veo3_video_prompt(idea.Idea, idea.Environment)
            log_entry['prompt'] = prompt
            
            # Log the initial entry and get the row index
            row_index = log_to_excel(log_entry)
            print(f"Log entry created with index: {row_index}")
            
            # Step 3: Submit to Gemini for storyboard generation
            generation_result = start_video_generation(prompt)

            if generation_result.get("status") != "completed":
                log_entry['status'] = "failed"
                log_entry['error'] = generation_result.get("error", "Unknown error")
                log_to_excel(log_entry, row_index)
                return None

            storyboard_text = generation_result.get("response", {}).get("text", "")
            log_entry['status'] = "completed"
            log_entry['gemini_output'] = storyboard_text
            print(f"Gemini output generated (truncated): {storyboard_text[:120]}...")
            
            # Step 4: Update the Excel log with final results
            log_to_excel(log_entry, row_index)
    except Exception as e:
        print(f"Error in workflow: {str(e)}")
        return None


async def main():
    # You can configure this to run on a schedule
    topic = "meteorologist woman chasing tornado live on air"  # Example topic
    
    # Number of ideas/storyboards to generate
    count = 1
    
    # Run main function
    await run_workflow(topic, count)
    

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if Gemini API key environment variable is set
    if not (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("KIE_API_TOKEN")
        or os.environ.get("KIE_API_KEY")
    ):
        print("Warning: GEMINI_API_KEY (or legacy KIE_API_TOKEN) environment variable not set")
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    asyncio.run(main())
