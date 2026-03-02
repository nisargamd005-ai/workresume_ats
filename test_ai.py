import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Load API key manually to verify
BASE_DIR = Path('c:/workresume_ats/workresume')
load_dotenv(BASE_DIR / '.env')
api_key = os.getenv('GEMINI_API_KEY')

print(f"DEBUG: Key from .env: {api_key[:10]}...")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

try:
    response = model.generate_content("Say 'Test Successful'")
    print(f"DEBUG: AI Response: {response.text}")
except Exception as e:
    print(f"DEBUG: AI Error: {e}")
