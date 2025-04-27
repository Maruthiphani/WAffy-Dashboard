import os
import html
from google.cloud import translate_v2 as translate
from dotenv import load_dotenv
import pycountry

load_dotenv()
TRANSLATOR_API_KEY_PATH = os.getenv("TRANSLATOR_API_KEY_PATH")

# Set the path to your JSON key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = TRANSLATOR_API_KEY_PATH

# Initialize Google Translate client
translate_client = translate.Client()

# Translate any text to English
def translate_to_english(text):
    result = translate_client.translate(text, target_language="en")
    return html.unescape(result["translatedText"])

# Detect the language of a given text
def detect_language(text):
    result = translate_client.detect_language(text)
    lang_code = result["language"]
    lang_name = pycountry.languages.get(alpha_2=lang_code)

    return lang_name.name if lang_name else lang_code  # Fallback to code if unknown

# Translate a message from Enlish to a target language.
def translate_to_language(text, target_lang):
    result = translate_client.translate(text, target_language=target_lang)
    return html.unescape(result["translatedText"])