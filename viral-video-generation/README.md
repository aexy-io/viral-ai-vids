# VEO3 Viral Videos Generator

### 👉 **READ MORE [Turn Any Topic Into Viral AI Videos Using Google's VEO3 Model!](https://dev.to/kaymen99/turn-any-topic-into-viral-ai-videos-using-googles-veo3-model-c03)**  

An AI automation tool that generates viral-worthy videos using Google's VEO3 model. This project allows you to automatically create high-quality, realistic AI videos from any topic.

**Check this meteorologist chasing a tornado short that I made 🚀**

https://github.com/user-attachments/assets/5521331c-a2ea-4f27-bd3a-f5a6a697be89

## Features

- **Topic-to-Video Pipeline**: Convert any topic into multiple creative video ideas with a single command
- **AI Idea Generation**: Uses **GPT-4.1-mini** to create viral-worthy video ideas with catchy captions
- **VEO3-Optimized Prompt Engineering**: Automatically crafts perfectly formatted prompts for Google's VEO3 model
- **Kie.ai Integration**: We use **Kie.ai API** to access Google's VEO3 without expensive subscriptions
- **Automated Runs**: can automate the process and log all video links to an Excel file

## How It Works

1. **Enter a topic** in the script (e.g., "Alien food critic reviewing Earth cuisine")
2. **First AI agent will generate creative ideas** with captions and the necessary video environment context
3. **A second AI agent will create VEO3-optimized prompts** including main character description, conversation, background, etc 
4. **We use Kie.ai API** to access the Google VEO3 model and we provide the generated prompts for video generation
5. **Scripts will wait for video processing** (typically takes 2-5 minutes)
6. At the end, **all generated videos URLs** will be saved to a local Excel file 

## Use Cases

- **Content Creation**: Generate engaging short videos for TikTok, Instagram Reels, YouTube Shorts
- **Marketing Campaigns**: Create promotional content with creative, eye-catching visuals
- **Concept Testing**: Quickly generate video prototypes to test ideas before full production
- **Social Media Management**: Automate the creation of multimedia content for multiple platforms
- **Education**: Create visually engaging explanatory videos for complex topics
- **Entertainment**: Generate fun, viral-worthy clips to build audience engagement

## How to run 

### Prerequisites

- Python 3.12 or higher
- Create an account on [Kie.ai](https://kie.ai) and get your API key
- [OpenRouter API key](https://openrouter.ai/) (to use any LLM model) or you preferred LLM API key, like OpenAI or Claude

### Project Structure

```
├── main.py           # Main script with the video generation workflow
├── prompts.py        # System prompts for LLM idea generation and prompt creation
├── utils.py          # Utility functions for API calls and data handling
├── requirements.txt  # Project dependencies
├── .env              # Environment variables (API keys, etc.)
└── videos.xlsx       # Generated Excel file with video metadata and URLs
```

### Setup

1. Clone the repository:
```bash
git clone https://github.com/kaymen99/viral-ai-vids
cd viral-ai-vids
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```
KIE_API_KEY=your_kie_ai_key_here
OPENROUTER_API_KEY=your_openrouter_key_here  # For LLM access
```

## Usage

1. Choose the topic of your videos and number of videos to generate in `main.py`:

```python
async def main():
    # Change this to whatever topic you'd like to explore
    topic = "Your creative topic here"  # e.g., "Alien food critic reviewing Earth cuisine"
    count = 1
    await run_workflow(topic, count)
```

2. Run the script:

```bash
python main.py
```

3. Check the generated Excel file (`videos.xlsx`) for video URLs and details.


## Notes

- **Google's VEO3 model via Kie.ai currently costs approximately $0.04 per second of video generated**
- **Videos are currently limited to 8 seconds in length**

## **Contact**

If you have any questions or suggestions, feel free to reach out!