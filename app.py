import streamlit as st
import re
import requests
import subprocess
import io
from PIL import Image
from gtts import gTTS
from inputs import (input1,input2,input4,input5)
from config import get_access_token ,Gemini_API_key
from tts_helper import detect_language,get_code_explanation,text_to_speech_google


# Set page config
st.set_page_config(page_title="CodeNova", layout="wide")


# Apply Dark Theme CSS
st.markdown(
    """
    <style>
        body {
            background-color: #121212;
            color: white;
        }
        .tool-card {
            background-color: #23272A;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
            transition: transform 0.2s ease-in-out;

        }
        .tool-card:hover {
            transform: scale(1.02);
        }
        h4 {
            color: white;
        }
        p, small {
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Navigation
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="https://i.imgur.com/GyI62fx.jpeg" width="150">
        
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.title("Navigation")

if "option" not in st.session_state:
    st.session_state.option = "Home"

if st.sidebar.button("Home"):
    st.session_state.option = "Home"

tool_option = st.sidebar.selectbox(
    "Tools:",
    ["Code Wizard", "Fix-It", "Code Whisperer",  
     "Code Optimizer", "DocuBot", "AI Pair Coder"],
    index=None if st.session_state.option == "Home" else 0
)

if tool_option and tool_option != st.session_state.option:
    st.session_state.option = tool_option
    st.rerun()

# Home Page
if st.session_state.option == "Home":
    st.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: center; gap: 1px;">
        <img src="https://i.imgur.com/BOFI56f.jpeg" alt="CodeNova Logo" style="height: 40px;display: inline-block;">
        <br><br><br>
    </div>
    """,
    unsafe_allow_html=True
    )

    st.write("An AI-driven platform that helps developers at every stage of the software lifecycle. From code generation and optimization to debugging and documentation, it enhances productivity, improves code quality, and streamlines workflows for faster, smarter development.")

    st.markdown(f"""
        <div>
            <h3>Available Tools</h3>
        </div>
        """, unsafe_allow_html=True
    )

    tools = [
        {"name": "Code Wizard", "desc": "Generate code in any programming language based on your description.", "provider": "AI Assistant"},
        {"name": "Fix-It", "desc": "Automatically debug and fix issues in your code.", "provider": "Debugger AI"},
        {"name": "Code Whisperer", "desc": "Get detailed explanations of your code in text or audio format.", "provider": "AI Explainer"},
        {"name": "Code Optimizer", "desc": "Refactor and Optimize your code to improve readability and efficiency.", "provider": "Performance AI"},
        {"name": "DocuBot", "desc": "Generate structured documentation for your code in TXT, DOCX, and PDF formats.", "provider": "Documentation AI"},
        {"name": "AI Pair Coder", "desc": "Collaborate with AI for real-time coding suggestions.", "provider": "AI Assistant"}
    ]

    cols = st.columns(2)
    for index, tool in enumerate(tools):
        with cols[index % 2]:
            st.markdown(f"""
            <div class="tool-card">
                <h4>{tool["name"]}</h4>
                <p><i>{tool["desc"]}<i></p>
                <small><b>Provider:</b> {tool["provider"]}</small>
            </div>
            """, unsafe_allow_html=True)

    st.write("---")
    st.write("Use the sidebar to navigate to different tools!")


# Code Generation Page
elif st.session_state.option == "Code Wizard":
    st.markdown(
    """
    <div style="position: absolute; top: 10px; right: 20px;">
        <img src="https://i.imgur.com/BOFI56f.jpeg" width="100">
    </div>
    """,
    unsafe_allow_html=True
    )


    st.title("Code Wizard")
    st.write("Generate code in any programming language based on your text input.")
    
    prompt = st.text_area("Enter your prompt:", placeholder="e.g., Create a function to add two numbers in Python")
    
    if st.button("Generate Code"):
        with st.spinner("Generating code..."):
            if prompt:
                access_token = get_access_token()
                
                # API endpoint and headers
                url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
                
                # API request body
                body = {
                    "input": f"Generate the required code for the following user task{prompt}",
                    "parameters": {
                        "decoding_method": "greedy",
                        "max_new_tokens": 2000,
                        "min_new_tokens": 0,
                        "repetition_penalty": 1.05
                    },
                    "model_id": "ibm/granite-34b-code-instruct",
                    "project_id": "71cf4fa0-b1a4-4b23-88a8-50171f7a92ee"
                }
                
                # Make the API request
                response = requests.post(url, headers=headers, json=body)
                
                # Handle the response
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    if results and "generated_text" in results[0]:
                        generated_text = results[0]["generated_text"].strip()
                        
                        # Extract code from the generated text
                        code_match = re.search(r"```(?:python|c\+\+|java|javascript)?\n(.*?)```", generated_text, re.DOTALL)
                        
                        if code_match:
                            generated_code = code_match.group(1).strip()  # Extract only the code
                        else:
                            generated_code = generated_text  # Use the entire text if no code block is found
                        
                        # Display the cleaned code 
                        st.code(generated_code)
                    else:
                        st.error("No valid response from model.")
                else:
                    st.error(f"Error: {response.status_code}, {response.text}")
            else:
                st.warning("Please enter a prompt.")

# Code Debugging Page
elif st.session_state.option == "Fix-It":
    st.markdown(
    """
    <div style="position: absolute; top: 10px; right: 20px;">
        <img src="https://i.imgur.com/BOFI56f.jpeg" width="100">
    </div>
    """,
    unsafe_allow_html=True
    )
    st.title("Fix-It")
    st.write("Debug your code and get suggestions for fixes.")
    
    code = st.text_area("Enter your code:", placeholder="Paste your code here")
    
    if st.button("Debug Code"):
        with st.spinner("Debugging code..."):
            if code:
                access_token = get_access_token()
                
                url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }   
                                
                body = {
                    "input": f"Debug and fix the following code and return the corrected code without any extra texts: {code}",
                    "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 2000,
                    "min_new_tokens": 0,
                    "stop_sequences": [],
                    "repetition_penalty": 1
                },
                "model_id": "ibm/granite-34b-code-instruct",
                "project_id": "33f5277e-ac20-4539-81fd-0ab8217c908f"
                }
                
                response = requests.post(url, headers=headers, json=body)
                
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    if results and "generated_text" in results[0]:
                        debug_output = results[0]["generated_text"].strip()
                        st.subheader("Corrected Code:")
                        st.code(debug_output)
                    else:
                        st.error("No valid response from model.")
                else:
                    st.error(f"Error: {response.status_code}, {response.text}")
            else:
                st.warning("Please enter some code to debug.")

# Code Explainer Page
elif st.session_state.option == "Code Whisperer":
    st.markdown(
    """
    <div style="position: absolute; top: 10px; right: 20px;">
        <img src="https://i.imgur.com/BOFI56f.jpeg" width="100">
    </div>
    """,
    unsafe_allow_html=True
    )
    st.title("Code Whisperer")
    st.write("Get a detailed explanation of your code in simple terms as text or audio file.")
    
    code = st.text_area("Enter your code:", placeholder="Paste your code here")
    
    if st.button("Generate Text Explanation"):
        with st.spinner("Explaining code..."):
            if code:
                access_token = get_access_token()
                
                url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
                
                body = {
                    "input": f"Your task is to analyze and explain the given code thoroughly and clearly.\n{code}\nExplanation:",
                    "parameters": {
                        "decoding_method": "greedy",
                        "max_new_tokens": 3000,
                        "min_new_tokens": 0,
                        "repetition_penalty": 1
                    },
                    "model_id": "ibm/granite-20b-code-instruct",
                    "project_id": "33f5277e-ac20-4539-81fd-0ab8217c908f"
                }
                
                response = requests.post(url, headers=headers, json=body)
                
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    if results and "generated_text" in results[0]:
                        explanation = results[0]["generated_text"].strip()
                        st.text_area("Explanation:", value=explanation, height=300)
                    else:
                        st.error("No valid response from model.")
                else:
                    st.error(f"Error: {response.status_code}, {response.text}")
            else:
                st.warning("Please enter some code to explain.")

    if st.button("Generate Audio Explanation"):
        with st.spinner("Explaining code..."):
            if code.strip():
                language_detected = detect_language(code)
                explanation = get_code_explanation(code, language_detected)
                
                if explanation:
                    audio_file = text_to_speech_google(explanation)
                    if audio_file:
                        st.subheader("Generated Audio Explanation:")
                        st.audio(audio_file, format="audio/mp3")
                        st.download_button(
                            label="Download as MP3",
                            data=open(audio_file, "rb").read(),
                            file_name="explanation.mp3",
                            mime="audio/mp3"
                        )
                    else:
                        st.error("Failed to generate audio file.")
            else:
                st.warning("Please enter some code before generating an explanation.")



# Code Refactoring Page
elif st.session_state.option == "Code Optimizer":
    st.markdown(
    """
    <div style="position: absolute; top: 10px; right: 20px;">
        <img src="https://i.imgur.com/BOFI56f.jpeg" width="100">
    </div>
    """,
    unsafe_allow_html=True
    )
    st.title("Code Optimizer")
    st.write("Refactor and Optimize your code to improve readability and efficiency.")
    
    code = st.text_area("Enter your code:", placeholder="Paste your code here")
    
    if st.button("Refactor Code"):
        with st.spinner("Refactoring code..."):
            if code:
                access_token = get_access_token()
                
                url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
                
                body = {
                    "input": f"{input4} and now the code to be refactored is {code}",
                    "parameters": {
                        "decoding_method": "greedy",
                        "max_new_tokens": 8000,
                        "min_new_tokens": 0,
                        "repetition_penalty": 1
                    },
                    "model_id": "ibm/granite-34b-code-instruct",
	                "project_id": "33f5277e-ac20-4539-81fd-0ab8217c908f"
                }
                
                response = requests.post(url, headers=headers, json=body)
                
                if response.status_code == 200:
                    response_data = response.json()
                    result= response_data.get("results", [{}])[0].get("generated_text", "No output generated.")
                    st.subheader("Corrected Code:")
                    st.code(result)

                else:
                    st.error(f"Error: {response.status_code}, {response.text}")
            else:
                st.warning("Please enter some code to refactor.")

# Automated Documentation Page
elif st.session_state.option == "DocuBot":
    st.markdown(
    """
    <div style="position: absolute; top: 10px; right: 20px;">
        <img src="https://i.imgur.com/BOFI56f.jpeg" width="100">
    </div>
    """,
    unsafe_allow_html=True
    )
    st.title("DocuBot")
    st.write("Generate documentation for your code automatically.")
    
    code = st.text_area("Enter your code:", placeholder="Paste your code here")
    
    if st.button("Generate Document"):
        with st.spinner("Generating documentation..."):
            if code:
                url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
                
                # Gemini API key
                gemini_api_key = f"{Gemini_API_key}"  
                
                headers = {
                    "Content-Type": "application/json"
                }
                
                body = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": f"{input5} And here is your code : {code}"
                                }
                            ]
                        }
                    ]
                }
                
                # Make the API request
                response = requests.post(
                    f"{url}?key={gemini_api_key}",
                    headers=headers,
                    json=body
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "candidates" in result and result["candidates"]:
                        documentation = result["candidates"][0]["content"]["parts"][0]["text"]
                        
                        st.text_area("Documentation:", value=documentation, height=400)
                        
                        st.markdown("### Download Documentation")
                    
                        # Download as TXT
                        st.download_button(
                            label="Download as TXT",
                            data=documentation,
                            file_name="documentation.txt",
                            mime="text/plain"
                        )
                        
                        # Download as DOCX 
                        try:
                            from docx import Document
                            doc = Document()
                            doc.add_paragraph(documentation)
                            doc_bytes = io.BytesIO()
                            doc.save(doc_bytes)
                            doc_bytes.seek(0)
                            
                            st.download_button(
                                label="Download as DOCX",
                                data=doc_bytes,
                                file_name="documentation.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        except ImportError:
                            st.warning("To download as DOCX, install the `python-docx` library: `pip install python-docx`")
                        
                        # Download as PDF 
                        try:
                            from reportlab.lib.pagesizes import letter
                            from reportlab.pdfgen import canvas
                            pdf_bytes = io.BytesIO()
                            c = canvas.Canvas(pdf_bytes, pagesize=letter)
                            text = c.beginText(40, 750)
                            for line in documentation.split("\n"):
                                text.textLine(line)
                            c.drawText(text)
                            c.save()
                            pdf_bytes.seek(0)
                            
                            st.download_button(
                                label="Download as PDF",
                                data=pdf_bytes,
                                file_name="documentation.pdf",
                                mime="application/pdf"
                            )
                        except ImportError:
                            st.warning("To download as PDF, install the `reportlab` library: `pip install reportlab`")
                    else:
                        st.error("No valid response from model.")
                else:
                    st.error(f"Error: {response.status_code}, {response.text}")
            else:
                st.warning("Please enter some code to generate documentation.")

# Pair Programming Page
elif st.session_state.option == "AI Pair Coder":
    st.markdown(
    """
    <div style="position: absolute; top: 10px; right: 20px;">
        <img src="https://i.imgur.com/BOFI56f.jpeg" width="100">
    </div>
    """,
    unsafe_allow_html=True
    )
    st.title("AI Pair Coder")
    st.write("Write your code below, and the AI will provide real-time suggestions and improvements as you type.")

    # Initialize session state for code
    if "code" not in st.session_state:
        st.session_state.code = ""

    # Text area for code input
    st.session_state.code = st.text_area(
        "Write your code here:",
        value=st.session_state.code,
        height=400,
        placeholder="Start typing your code...",
        key="code_input"
    )

    # Function to get AI suggestions
    def get_ai_suggestions(code):
        access_token = get_access_token()

        url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        body = {
            "input": f"Review the following code and provide suggestions for improvements or fixes: {code}",
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 500,
                "min_new_tokens": 0,
                "repetition_penalty": 1.05
            },
            "model_id": "ibm/granite-34b-code-instruct",
            "project_id": "71cf4fa0-b1a4-4b23-88a8-50171f7a92ee"
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            results = response.json().get("results", [])
            if results and "generated_text" in results[0]:
                return results[0]["generated_text"].strip()
            else:
                return "No suggestions available."
        else:
            return f"Error: {response.status_code}, {response.text}"

    # Real-time suggestion 
    if st.session_state.code:
        with st.spinner("AI is analyzing your code..."):
            suggestions = get_ai_suggestions(st.session_state.code)
            st.subheader("AI Suggestions:")
            st.code(suggestions)
    else:
        st.warning("Please start typing your code to get AI suggestions.")
