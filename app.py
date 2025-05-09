import streamlit as st
import base64
from pathlib import Path
import google.generativeai as genai
from PIL import Image
import io
try:
    from api_key import api_key
except ImportError:
    api_key = None

# Configure the page
st.set_page_config(
    page_title="MediAI VitalImage Analytics",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match MediAI theme
def apply_custom_css():
    st.markdown("""
    <style>
    :root {
        --primary: #FFE6E6;
        --primary-light: #4FC1AF;
        --secondary: #CC543F;
        --accent: #00C9A7;
        --light: #33AB9F;
        --dark: #001919;
        --gray: #666;
        --white: #fff;
        --background: #f9f9f9;
        --text: #333;
    }
    
    .stApp {
        background-color: var(--background);
        color: var(--text);
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    h1, h2, h3 {
        color: var(--accent);
    }
    
    .stButton > button {
        background-color: var(--accent);
        color: white;
        border-radius: 30px;
        font-weight: 600;
        padding: 0.5rem 2rem;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: var(--primary-light);
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0, 201, 167, 0.3);
    }
    
    .uploadedFileData {
        border-radius: 20px;
        overflow: hidden;
    }
    
    .stImage img {
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    .css-1kyxreq {
        justify-content: center;
    }
    
    .feature-card {
        background-color: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .feature-card:hover {
        transform: translateY(-10px);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        color: var(--accent);
    }
    
    .footer {
        background-color: var(--dark);
        color: white;
        padding: 2rem;
        text-align: center;
        border-radius: 20px;
        margin-top: 2rem;
    }

    .stProgress .st-bo {
        background-color: var(--accent);
    }

    .step-card {
        background-color: var(--primary);
        border-radius: 20px;
        padding: 1rem;
        margin-bottom: 1rem;
        position: relative;
    }

    .step-number {
        position: absolute;
        top: -15px;
        left: -15px;
        width: 40px;
        height: 40px;
        background-color: var(--accent);
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        font-weight: 700;
    }

    .results-container {
        background-color: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
    }
    
    /* Logo styling */
    .logo {
        display: flex;
        align-items: center;
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent);
        margin-bottom: 1rem;
    }
    
    .logo span {
        color: var(--secondary);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Function to encode image to base64
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Function to create a placeholder image
def placeholder_image(width, height, text="MediAI"):
    img = Image.new('RGB', (width, height), color=(0, 201, 167))
    return img

# Function to create a feature card
def feature_card(icon, title, description):
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-icon">{icon}</div>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)

# Function to create a step card
def step_card(number, title, description):
    st.markdown(f"""
    <div class="step-card">
        <div class="step-number">{number}</div>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)

# Apply custom CSS
apply_custom_css()

# Create a session state to store the analysis results and API key
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = ""

# Configure Gemini API with imported API key
def initialize_genai():
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

# Initialize the API with the imported key
api_configured = initialize_genai()

# Logo and title
st.markdown('<div class="logo">Medi<span>AI</span> VitalImage Analytics</div>', unsafe_allow_html=True)
st.markdown("### AI-Powered Medical Image Analysis")

# Create a layout with two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("## Upload Medical Image")
    
    # API key status
    if not api_configured:
        st.error("API key not found. Please check that your api_key.py file contains a valid Google API key.")
        st.stop()
    
    # Image upload section
    uploaded_file = st.file_uploader("Select a medical image to analyze", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        # Additional context input
        context = st.text_area("Provide any additional context or information about the image (optional)")
        
        # Analysis button
        if st.button("Run Analysis"):
            if not api_configured:
                st.error("Please configure your Google AI API key to proceed")
            else:
                with st.spinner("Analyzing image..."):
                    try:
                        # Use the correct model name for Gemini 2.0 Flash
                        model_name = "gemini-1.5-flash"
                        
                        # Generation config
                        generation_config = {
                            "temperature": 0.4,
                            "top_p": 0.95,
                            "top_k": 40,
                            "max_output_tokens": 4096,
                        }
                        
                        # System prompt for medical image analysis
                        system_prompt = """
                        You are a highly skilled medical practitioner specializing in image analysis. Provide a detailed analysis of the uploaded medical image with the following structure:

                        1. IMAGE SUMMARY: Brief description of what is visible in the image
                        2. DETAILED ANALYSIS: In-depth examination of visible features, abnormalities, or patterns
                        3. POTENTIAL FINDINGS: Possible medical conditions or diagnoses suggested by the image
                        4. RECOMMENDATIONS: Suggested next steps for the patient
                        5. LIMITATIONS: Any limitations in your analysis due to image quality or type

                        If you cannot provide a reliable medical analysis due to image constraints, clearly state this limitation. Always maintain a professional medical tone and emphasize that this analysis should not replace proper medical consultation.
                        """
                        
                        # Initialize model
                        model = genai.GenerativeModel(
                            model_name=model_name,
                            generation_config=generation_config,
                        )
                        
                        # Prepare image data
                        image_bytes = uploaded_file.getvalue()
                        
                        # Add context to prompt if provided
                        prompt_text = system_prompt
                        if context:
                            prompt_text += f"\n\nAdditional context provided: {context}"
                        
                        # Generate analysis
                        response = model.generate_content(
                            [
                                prompt_text,
                                {"mime_type": f"image/{uploaded_file.type.split('/')[1]}", "data": image_bytes}
                            ]
                        )
                        
                        # Store results in session state
                        st.session_state.analysis_results = response.text
                        st.session_state.analysis_complete = True
                        
                    except Exception as e:
                        st.error(f"An error occurred during analysis: {str(e)}")
                        st.info("If you're seeing model not found errors, make sure you're using a valid API key with access to the Gemini models.")
    
    # How it works section
    st.markdown("## How It Works")
    
    step_card("1", "Upload Image", "Upload any medical image you want to analyze.")
    step_card("2", "Add Context", "Provide any relevant information about the image.")
    step_card("3", "AI Analysis", "Our advanced AI examines the image for patterns and indicators.")
    step_card("4", "Review Results", "Get detailed analysis and recommendations.")

with col2:
    # Display analysis results if available
    if st.session_state.analysis_complete:
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        st.markdown("## Analysis Results")
        st.markdown(st.session_state.analysis_results)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Reset button
        if st.button("Start New Analysis"):
            st.session_state.analysis_complete = False
            st.session_state.analysis_results = ""
            st.rerun()
    else:
        # Show features when no analysis is running
        st.markdown("## Key Features")
        
        feature_card("🔍", "Symptom Analysis", "Our AI system analyzes your medical images to identify potential health issues.")
        feature_card("📷", "Multi-format Support", "Upload X-rays, MRIs, CT scans, ultrasounds, and more.")
        feature_card("🧠", "Advanced AI", "Powered by state-of-the-art generative AI models trained on medical data.")
        feature_card("📋", "Comprehensive Reports", "Get detailed analysis reports with potential findings and recommendations.")

# Footer
st.markdown("""
<div class="footer">
    <p>&copy; 2025 MediAI VitalImage Analytics. All Rights Reserved.</p>
    <p>This tool is for informational purposes only and should not replace professional medical advice.</p>
</div>
""", unsafe_allow_html=True)

# Disclaimer
with st.sidebar:
    st.image(placeholder_image(200, 100), caption="")
    st.markdown('<div class="logo">Medi<span>AI</span></div>', unsafe_allow_html=True)
    st.markdown("### Medical Image Analysis")
    
    st.markdown("---")
    
    st.markdown("""
    ### How to use:
    1. Upload your medical image
    2. Add any relevant context
    3. Click "Run Analysis"
    4. Review the AI-generated findings
    """)
    
    st.markdown("---")
    
    st.warning("""
    **IMPORTANT DISCLAIMER**
    
    This tool provides automated analysis of medical images and is intended for informational purposes only. It should not be considered medical advice, diagnosis, or treatment recommendation.
    
    Always consult with a qualified healthcare professional for proper medical evaluation and advice.
    """)

