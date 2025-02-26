import os
import requests
import streamlit as st

#Gemini key
Gemini_API_key=st.secrets["GEMINI_API_KEY"]
# IBM Cloud API Key
API_KEY = st.secrets["IBM_CLOUD_API_KEY"]

# IAM token endpoint
IAM_URL = "https://iam.cloud.ibm.com/identity/token"

# Function to generate access token
def get_access_token():
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": API_KEY
    }
    response = requests.post(IAM_URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Error generating access token: {response.status_code}, {response.text}")
