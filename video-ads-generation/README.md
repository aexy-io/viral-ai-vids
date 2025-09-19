# 🎬 AI Video Ads Generator

### 👉 **READ MORE: [Create Viral AI Marketing Ads for Almost Nothing with VEO3](https://dev.to/kaymen99/create-viral-ai-marketing-ads-for-almost-nothing-with-veo3-3o35)**  

### 🚀 **Want to try it out?** Test the live demo [VEO3 Ads Generator](https://veo3-ads-generator.streamlit.app/)

A complete system for generating professional marketing video storyboards using Google Gemini. Craft viral-quality scene plans for any brand or product in seconds, with a user-friendly Streamlit interface and curated prompt library ready for tools like VEO3, Runway, or Pika.

▶️ **See the ad I generated in seconds** for *“Mercedes F1 Car Launch”* — made entirely with VEO3. You won’t believe it’s AI:

[![VEO3 Ads Generator](https://github.com/user-attachments/assets/68e00228-b782-4e7f-b104-88c4ddd6f159)](https://www.youtube.com/watch?v=jodrXBd4DRo)

## Features

- **🎨 Curated Prompt Library**: Collection of high-performing VEO3 prompts from viral Twitter ads (IKEA, Tesla, Nike, Jeep, etc.)
- **🤖 AI-Powered Prompt Generation**: Uses GPT-4 to transform your brand ideas using inspiration from the prompt library
- **📱 Streamlit Web Interface**: User-friendly app for non-technical users with API key management
- **⚙️ Flexible Configuration**: Choose Gemini model (flash/pro), aspect ratio guidance (16:9/9:16), and prompt inspiration
- **📊 Excel Logging**: Automatic tracking of generated prompts, Gemini storyboards, and metadata
- **💰 Cost-Effective**: Generate professional marketing storyboards instantly with Gemini
- **🔧 Developer-Friendly**: Complete Python codebase with LangChain integration for multiple LLM providers

## How It Works

### 📱 Streamlit Web App (Recommended)
1. **Enter your video idea** (e.g., "Mercedes luxury car ad showing performance")
2. **Select prompt inspiration** from the curated library (IKEA, Tesla, Nike, etc.)
3. **Choose settings**: Gemini model (flash/pro) and aspect ratio (16:9/9:16)
4. **AI generates optimized prompt** using GPT-4 based on your idea and selected inspiration
5. **Storyboard generation** via Google Gemini (JSON formatted scene plan)
6. **Copy the storyboard** into your preferred video generation service to render the final video

### 💻 Command Line (For Developers)
1. **Configure your brand idea** in `main.py`
2. **Select inspiration prompt** from the prompt library
3. **Run the workflow**: `python main.py`
4. **All results saved** to Excel file with prompts, storyboards, and metadata 

## Use Cases

- **📱 Social Media Marketing**: Create viral-quality ads for TikTok, Instagram Reels, YouTube Shorts
- **🏢 Small Business Advertising**: Generate professional marketing videos without expensive production costs
- **🎨 Marketing Agencies**: Scale video production for multiple clients efficiently
- **🛍️ E-commerce Product Ads**: Showcase products with cinematic quality demonstrations
- **🚗 Brand Campaigns**: Create compelling brand stories and product launches
- **🎯 A/B Testing**: Quickly generate multiple video variations to test messaging
- **💼 Corporate Marketing**: Professional video content for presentations and campaigns
- **🚀 Startup Marketing**: Cost-effective way to create high-quality promotional content

## How to run 

### Prerequisites

- Python 3.12 or higher
- Create an API key for [Google Gemini](https://ai.google.dev/) (used for storyboard generation)
- [OpenRouter API key](https://openrouter.ai/) (to use any LLM model) or you preferred LLM API key, like OpenAI or Claude

### Project Structure

```
├── streamlit_app.py     # Streamlit web interface (recommended)
├── main.py              # Command-line workflow for developers
├── prompts.py           # Curated VEO3 prompt library from viral Twitter ads
├── prompt_library.py    # Prompt metadata and library management
├── video_gen.py         # Gemini API integration for storyboard generation
├── utils.py             # Utility functions for LLM calls and Excel logging
├── requirements.txt     # Project dependencies
├── .env                 # Environment variables (API keys, etc.)
└── videos.xlsx          # Generated Excel file with video metadata and URLs
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
GEMINI_API_KEY=your_gemini_key_here
OPENROUTER_API_KEY=your_openrouter_key_here  # For LLM access
```

## Usage

### 📱 Option 1: Streamlit Web App (Recommended)

1. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

2. Open your browser and:
   - Add your API keys in the sidebar
   - Enter your video idea (e.g., "Mercedes luxury car commercial")
   - Select prompt inspiration from the library
   - Choose Gemini model and aspect ratio guidance
   - Click "Generate Storyboard"
   - Copy the storyboard JSON into your preferred video generation tool (e.g., VEO3)

### 💻 Option 2: Command Line (For Developers)

1. Configure your brand idea in `main.py`:

```python
async def main():
    inputs = {
        "ad_idea": "Your brand/product idea here",
        "inspiration_prompt": selected_prompt['prompt'],  # From prompt library
        "aspect_ratio": "16:9",  # or "9:16"
        "model": "gemini-1.5-flash"  # or "gemini-1.5-pro"
    }
    result = await run_workflow(inputs)
```

2. Run the script:
```bash
python main.py
```

3. Check the generated Excel file (`ad_videos.xlsx`) for prompts, storyboards, and metadata.


## 💰 Pricing & Notes

- **Gemini Storyboard Generation**: Included with your Google AI Studio usage (text tokens only)
- **Prompt Generation (GPT-4.1)**: ~$0.02 per request via OpenRouter (configurable)
- **Video Rendering**: Bring your own video generator (e.g., VEO3, Pika, Runway). Costs depend on your chosen tool.
- **Tip**: Use the JSON storyboard to drive scene-by-scene prompts in your preferred video service.

## 🚀 What Makes This Special

- **Curated Prompt Library**: Hand-collected from viral Twitter VEO3 ads
- **Structured Prompts**: Uses JSON/YAML formatting that VEO3 understands best
- **Community-Driven**: Built on prompts shared by the VEO3 community
- **Cost-Effective**: Professional video production for under $1
- **User-Friendly**: Both technical (CLI) and non-technical (Streamlit) interfaces

## 🔗 Links

- **Google Gemini**: [Official documentation](https://ai.google.dev/)
- **OpenRouter**: [Multi-LLM API access](https://openrouter.ai)

## **Contact**

If you have any questions or suggestions, feel free to reach out!

---

**⭐ If this project helped you create amazing marketing videos, please give it a star!**
