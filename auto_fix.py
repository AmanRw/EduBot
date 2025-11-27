import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
# Use getattr to access functions to avoid static-analysis warnings when
# the package uses dynamic exports. This also provides a clear runtime
# error if the expected API is missing.
configure = getattr(genai, "configure", None)
if configure is None:
    raise RuntimeError("google.generativeai.configure is not available in the installed package")
configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("🔍 Searching for valid models...")

valid_models = []
list_models = getattr(genai, "list_models", None)
if list_models is None:
    raise RuntimeError("google.generativeai.list_models is not available in the installed package")
for m in list_models():
    if 'generateContent' in getattr(m, 'supported_generation_methods', []):
        valid_models.append(getattr(m, 'name', None))

if not valid_models:
    print("❌ No models found. Your API Key may be invalid or inactive.")
else:
    print(f"✅ Found {len(valid_models)} models.")
    print(f"   Recommended: {valid_models[0]}")
    print("\nPaste this EXACT line into src/config.py:")
    # Remove 'models/' prefix if present, as LangChain adds it automatically sometimes
    clean_name = valid_models[0].replace("models/", "")
    print(f'    MODEL_NAME = "{clean_name}"')