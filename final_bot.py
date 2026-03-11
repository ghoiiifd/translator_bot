import os
import time
import telebot
import pdfplumber
from google import genai
from google.genai.errors import ClientError
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ---------- Config ----------
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8761170089:AAF3dOFS9BftYErhtUYiwdcbujkUBzhzgEs')

# Multiple Gemini API keys for rotation
GEMINI_KEYS = [
        os.environ.get('GEMINI_API_KEY_1', 'AIzaSyAjjGymZwdXjr1TW1ssmQBhdK255gSpZ9E'),
            os.environ.get('GEMINI_API_KEY_2', ''),
                os.environ.get('GEMINI_API_KEY_3', ''),
]
GEMINI_KEYS = [k for k in GEMINI_KEYS if k]

current_key_index = 0

def get_client():
        return genai.Client(api_key=GEMINI_KEYS[current_key_index])

        bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

        def translate_text(text):
                global current_key_index
                    if not text or len(text.strip()) < 3:
                                return ''
                                    prompt = (
                                                "You are an expert academic translator. "
                                                        "Translate the following scientific text from English to Arabic contextually. "
                                                                "Return only the Arabic translation, nothing else:\n\n" + text
                                    )
                                        for attempt in range(len(GEMINI_KEYS) * 2):
                                                    try:
                                                                    client = get_client()
                                                                                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                                                                                            return response.text.strip()
                                                                                                    except ClientError as e:
                                                                                                                    if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
                                                                                                                                        current_key_index = (current_key_index + 1) % len(GEMINI_KEYS)
                                                                                                                                                        time.sleep(2)
                                                                                                                                                                    else:
                                                                                                                                                                                        return '[Translation Error]'
                                                                                                                                                                                                except Exception as e:
                                                                                                                                                                                                                time.sleep(3)
                                                                                                                                                                                                                    return '[Quota Exceeded]'

                                                                                                                                                                                                                    def process_do
                                    )
]