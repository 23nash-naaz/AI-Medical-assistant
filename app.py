import streamlit as st
from pathlib import Path
import google.generativeai as genai

from api_key import api_key

genai.configure(api_key=api_key)
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
system_prompt = """
An AI-powered tool for medical image analysis, as a highly skilled medical practitioner specializing in image analysis, I can help you understand the details of the image you upload. Please upload the medical image you would like me to analyze.

Your responsibilities include:
1. Uploading the medical image.
2. Providing any relevant context or information about the image.
3.Detailed Analysis
4.Finding reports
5.Recommendations and next steps
6. Treatment suggestions
"""
model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
)

# chat_session = model.start_chat(
#   history=[
#     {
#       "role": "user",
#       "parts": [
#         files[0],
#         "what's going on here",
#       ],
#     },
#     {
#       "role": "model",
#       "parts": [
#         "The image shows a cartoon-style illustration of a young woman in a thoughtful pose. Here's a breakdown of what's going on in the image:\n\n*   **Subject:** A young woman with auburn (reddish-brown) hair and blue eyes.\n*   **Pose:** She has her finger to her lip, and her eyes are looking upwards, which is a common gesture indicating thoughtfulness or contemplation.\n*   **Facial expression:** She seems to be in deep thought.\n*   **Background:** The background is a plain, light pink color with a shadow of the woman and a question mark.\n*   **Question mark:** A question mark hovers above her head, visually representing that she is pondering something.\n\nIn essence, the image is a representation of someone who is thinking, questioning, or trying to figure something out.",
#       ],
#     },
#   ]
# )

st.set_page_config(page_title="VitalImage Analytics", page_icon="🧠", layout="centered", initial_sidebar_state="expanded")
st.image(r"C:\Users\NASHRAH\OneDrive\Pictures\Screenshots\Screenshot 2024-08-29 215913.png", width=200)
st.title("👩‍🎨 Vital 🚑 Image 🫀 Analysis 💖")

st.subheader("An AI-powered tool for medical image analysis")
uploaded_file = st.file_uploader("Upload the medical image for analysis", type=["jpg", "jpeg", "png"])
if uploaded_file:
    st.image(uploaded_file, width=250,caption="Uploaded Image")
submit_button=st.button("Run Analysis")

if submit_button:
    image_data=uploaded_file.getvalue()

    image_parts=[
        {
            "mime_type": "image/jpeg",
            "data": image_data,
        },
    ]
    prompt_parts=[
        image_parts[0],
        system_prompt,
    ]
    st.image(image_data,width=250)
    st.title("HERE IS THE ANALYSIS BASED ON THE IMAGE YOU UPLOADED")
    response = model.generate_content(prompt_parts)

    st.write(response.text)

