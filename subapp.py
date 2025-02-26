import streamlit as st
import requests
from config import get_access_token

# Set page config
st.set_page_config(page_title="AI-Powered Pair Programming", layout="wide")

st.sidebar.title("Navigation")
option = st.sidebar.selectbox(
    "Choose a tool:",
    ["Home", "Code Generation", "Code Debugging", "Code Explainer", 
     "Code Refactoring", "Automated Documentation", "Pair Programming"]
)


# Home Page
if option == "Home":
    st.title("AI-Powered Software Engineering Tool")
    st.write("Welcome to the AI-powered software engineering tool! Use the sidebar to navigate to different features.")
    st.image("https://via.placeholder.com/800x400.png?text=AI+Software+Engineering+Tool", use_column_width=True)

# Pair Programming Page
elif option == "Pair Programming":
    st.title("AI-Powered Pair Programming")
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
        # Generate access token dynamically
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

        # Make the API request
        response = requests.post(url, headers=headers, json=body)

        # Handle the response
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results and "generated_text" in results[0]:
                return results[0]["generated_text"].strip()
            else:
                return "No suggestions available."
        else:
            return f"Error: {response.status_code}, {response.text}"

    # Real-time suggestion logic
    if st.session_state.code:
        with st.spinner("AI is analyzing your code..."):
            # Get AI suggestions
            suggestions = get_ai_suggestions(st.session_state.code)

            # Display suggestions
            st.subheader("AI Suggestions:")
            st.code(suggestions, language="python")  # Use "python" or "cpp" based on your code
    else:
        st.warning("Please start typing your code to get AI suggestions.")