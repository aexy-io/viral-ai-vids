import os
import pandas as pd
from langchain_openai import ChatOpenAI
from datetime import datetime


# Excel file for logging
EXCEL_LOG_FILE = "videos.xlsx"

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

async def ainvoke_llm(
    model,  # Specify the model name from OpenRouter
    system_prompt,
    user_message,
    response_format=None,
    temperature=0.1
):
    llm = ChatOpenAI(
        model=model, 
        temperature=temperature,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
    )
    
    # If Response format is provided, use structured output
    if response_format:
        llm = llm.with_structured_output(response_format)
    
    # Prepare messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    # Invoke LLM asynchronously
    response = await llm.ainvoke(messages)
    
    return response if response_format else response.content  # Return structured response or string

def log_to_excel(data, row_index=None):
    """
    Log video generation data to Excel file.
    If row_index is provided, updates an existing row instead of creating a new one.
    Returns the DataFrame index of the entry (new or updated).
    """
    expected_columns = [
        'idea', 'caption', 'environment', 'prompt',
        'status', 'task_id', 'video_url', 'gemini_output', 'error', 'created_at'
    ]

    if os.path.exists(EXCEL_LOG_FILE):
        df = pd.read_excel(EXCEL_LOG_FILE)
        for column in expected_columns:
            if column not in df.columns:
                df[column] = ""
    else:
        df = pd.DataFrame(columns=expected_columns)
    
    if row_index is not None and 0 <= row_index < len(df):
        # Update existing row
        for key, value in data.items():
            df.loc[row_index, key] = value
    else:
        # Create new row
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        row_index = len(df) - 1  # Get the index of the newly added row
    
    # Save to Excel
    df.to_excel(EXCEL_LOG_FILE, index=False)
    return row_index
