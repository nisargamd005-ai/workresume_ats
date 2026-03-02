import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path('c:/workresume_ats/workresume')
load_dotenv(BASE_DIR / '.env')
api_key = os.getenv('GEMINI_API_KEY')

print(f"DEBUG: Testing Key: {api_key[:10]}...")
genai.configure(api_key=api_key)

test_models = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.0-pro", "gemini-2.0-flash-exp", "gemini-2.0-flash-lite"]

for m_name in test_models:
    print(f"--- Testing {m_name} ---")
    try:
        model = genai.GenerativeModel(m_name)
        response = model.generate_content("Hi, say OK if you hear me.")
        print(f"SUCCESS with {m_name}: {response.text.strip()}")
        break # Found one!
    except Exception as e:
        print(f"FAIL with {m_name}: {e}")
