import streamlit as st
import asyncio
import os
from typing import Dict, Any
from prompt_library import PROMPT_LIBRARY
from main import run_workflow
import json

# Configure the Streamlit page
st.set_page_config(
    page_title="AI Storyboard Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def set_api_keys(gemini_key: str):
    """Set API keys as environment variables"""
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
        # Backwards compatibility for legacy environment variables
        os.environ["KIE_API_TOKEN"] = gemini_key

def validate_api_keys() -> bool:
    """Check if required API keys are set"""
    return bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("KIE_API_TOKEN"))

def display_storyboard(output_text: str, title: str):
    """Display the generated storyboard or plan from Gemini."""
    if not output_text:
        st.error("❌ Failed to generate storyboard or Gemini returned empty output")
        return

    st.success("✅ Storyboard generated successfully!")
    st.subheader(f"🎬 {title}")

    try:
        storyboard = json.loads(output_text)
        st.json(storyboard, expanded=False)
    except json.JSONDecodeError:
        st.text_area("Gemini Output", value=output_text, height=300, disabled=True)

def main():
    # Sidebar for API keys
    with st.sidebar:
        st.header("🔑 API Configuration")
        st.markdown("Enter your API keys to get started:")
        
        gemini_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Your Google Gemini API key for storyboard generation"
        )
        
        if st.button("Save", type="primary"):
            set_api_keys(gemini_key)
            if validate_api_keys():
                st.success("✅ API keys saved successfully!")
            else:
                st.error("❌ Please provide a Gemini API key")

    # Main content area
    st.title("🎬 AI Storyboard Generator")
    st.markdown("Generate detailed AI video storyboards with customizable prompts and settings")

    # Check if API keys are configured
    if not validate_api_keys():
        st.warning("⚠️ Please configure your Gemini API key in the sidebar before proceeding.")
        st.stop()

    # Video idea input
    st.header("💡 Video Idea")
    video_idea = st.text_area(
        "Describe your video concept:",
        placeholder="e.g., I want an ad for a Mercedes car showing luxury and performance",
        height=100
    )

    # Prompt inspiration selection
    st.header("🎨 Prompt Inspiration")
    st.markdown("Choose one or more prompt templates to inspire your video:")
    
    # Create a more user-friendly prompt selection
    prompt_options = []
    for i, prompt in enumerate(PROMPT_LIBRARY):
        prompt_options.append({
            "index": i,
            "display": f"{prompt['name']} - {prompt['description'][:100]}{'...' if len(prompt['description']) > 100 else ''}",
            "name": prompt['name'],
            "description": prompt['description']
        })
    
    # Single select for prompts
    selected_prompt_display = st.selectbox(
        "Select prompt inspiration:",
        options=[opt["display"] for opt in prompt_options],
        help="Choose one prompt template to inspire your video"
    )
    
    # Get selected prompt
    selected_prompt = None
    if selected_prompt_display:
        for opt in prompt_options:
            if opt["display"] == selected_prompt_display:
                selected_prompt = PROMPT_LIBRARY[opt["index"]]
                break

    # Display selected prompt details
    if selected_prompt:
        st.subheader("📋 Selected Prompt Details")
        with st.expander(f"🎯 {selected_prompt['name']}"):
            st.markdown(f"**Description:** {selected_prompt['description']}")
            st.markdown(f"**Source:** {selected_prompt['source']}")
            
            # Show a preview of the prompt structure
            if isinstance(selected_prompt['prompt'], dict):
                st.json(selected_prompt['prompt'], expanded=False)

    # Video settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("📐 Resolution")
        aspect_ratio = st.selectbox(
            "Choose aspect ratio:",
            options=["16:9", "9:16"],
            help="16:9 for landscape videos, 9:16 for vertical/mobile videos"
        )
    
    with col2:
        st.header("🚀 Gemini Model")
        model = st.selectbox(
            "Choose Gemini model:",
            options=["gemini-1.5-flash", "gemini-1.5-pro"],
            help="gemini-1.5-flash is faster, gemini-1.5-pro provides more detailed outputs"
        )

    # Generate button
    st.markdown("---")
    
    if not video_idea.strip():
        st.warning("⚠️ Please enter a video idea to proceed.")
    elif not selected_prompt:
        st.warning("⚠️ Please select a prompt inspiration.")
    else:
        if st.button("📝 Generate Storyboard", type="primary", use_container_width=True):
            # Use the selected prompt
            inspiration_prompt = selected_prompt['prompt']
            
            # Prepare inputs for the workflow
            inputs = {
                "ad_idea": video_idea,
                "inspiration_prompt": inspiration_prompt,
                "aspect_ratio": aspect_ratio,
                "model": model
            }
            print(f"Inputs: {inputs}")
            
            # Show progress
            with st.spinner("🔄 Generating your storyboard..."):
                st.info("Storyboards are generated instantly. You can paste them into your preferred video generation tool.")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Update progress
                    progress_bar.progress(10)
                    status_text.text("📝 Creating video prompt...")
                    
                    # Run the workflow
                    result = asyncio.run(run_workflow(inputs))
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Storyboard generation completed!")
                    
                    if result:
                        # Display the result
                        st.balloons()
                        display_storyboard(result.get("gemini_output", ""), result.get("title", "Generated Storyboard"))
                        
                        # Show generated prompt details
                        with st.expander("📄 Generated Prompt Details"):
                            st.markdown(f"**Title:** {result.get('title', 'N/A')}")
                            st.markdown("**Generated Prompt:**")
                            st.text_area("", value=result.get('prompt', 'N/A'), height=200, disabled=True)
                    else:
                        st.error("❌ Failed to generate storyboard. Please check the logs for more details.")
                        
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    st.markdown("Please check your API keys and try again.")
                
                finally:
                    progress_bar.empty()
                    status_text.empty()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>📝 AI Storyboard Generator powered by Gemini</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
