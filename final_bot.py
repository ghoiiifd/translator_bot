import os
import time
import telebot
import pdfplumber
from google import genai
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

TELEGRAM_BOT_TOKEN = '8761170089:AAF3dOFS9BftYErhtUYiwdcbujkUBzhzgEs'
GEMINI_KEYS = [k for k in [os.environ.get('GEMINI_API_KEY', ''), os.environ.get('GEMINI_API_KEY_1', '')] if k]
if not GEMINI_KEYS: GEMINI_KEYS = ['AIzaSyAlxMiRdNW232qurvyZCvde_FbFilpUTao']

key_index = 0
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def translate_text(text):
              global key_index
              if not text or len(text.strip()) < 3: return ''
                            prompt = 'Translate English to Arabic. Return only Arabic:\n' + text
  for _ in range(len(GEMINI_KEYS) * 2):
                  try:
                                    client = genai.Client(api_key=GEMINI_KEYS[key_index])
                                    res = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                                    return res.text.strip()
                                  except:
      key_index = (key_index + 1) % len(GEMINI_KEYS)
      time.sleep(2)
  return 'Error'

def process_file(inp, out, is_docx):
              new_doc = Document()
  if is_docx:
                  doc = Document(inp)
                  for p in doc.paragraphs:
                                    if p.text.strip():
                                                        new_doc.add_paragraph(p.text)
                                                        new_doc.add_paragraph(translate_text(p.text))
  else:
    with pdfplumber.open(inp) as pdf:
                      for page in pdf.pages:
                                          txt = page.extract_text()
                                          if txt:
                                                                for b in txt.split('\n\n'):
                                                                                        new_doc.add_paragraph(b)
                                                                                        new_doc.add_paragraph(translate_text(b))
                                                                              new_doc.save(out)

                                  @bot.message_handler(commands=['start'])
def welcome(message): bot.reply_to(message, 'Welcome!')

@bot.message_handler(content_types=['document'])
def handle_docs(message):
              ext = os.path.splitext(message.document.file_name)[1].lower()
  if ext not in ['.pdf', '.docx']: return
                bot.reply_to(message, 'Translating...')
  try:
                  data = bot.download_file(bot.get_file(message.document.file_id).file_path)
    inp, out = f'in{ext}', 'out.docx'
    with open(inp, 'wb') as f: f.write(data)
                    process_file(inp, out, ext == '.docx')
    bot.send_document(message.chat.id, open(out, 'rb'))
    os.remove(inp)
    os.remove(out)
except Exception as e: bot.reply_to(message, f'Error: {e}')

if __name__ == '__main__': bot.infinity_polling()
            
