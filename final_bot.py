import os
import telebot
import pdfplumber
from google import genai
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ---------- Config ----------
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8761170089:AAF3dOFS9BftYErhtUYiwdcbujkUBzhzgEs')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyAjjGymZwdXjr1TW1ssmQBhdK255gSpZ9E')

# New Google GenAI client
client = genai.Client(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# ---------- Translation ----------
def translate_text(text):
    if not text or len(text.strip()) < 3:
        return ''
    prompt = (
        "You are an expert academic translator. "
        "Translate the following scientific text from English to Arabic contextually. "
        "Return only the Arabic translation, nothing else:\n\n" + text
    )
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"[Translation Error]: {e}")
        return '[خطأ في الترجمة]'

# ---------- DOCX Processing ----------
def process_docx(input_path, output_path):
    doc = Document(input_path)
    new_doc = Document()
    for para in doc.paragraphs:
        if para.text.strip():
            # Original English paragraph
            new_doc.add_paragraph(para.text)
            # Arabic translation directly below
            ar = translate_text(para.text)
            ar_para = new_doc.add_paragraph(ar)
            ar_para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            new_doc.add_paragraph('')
    new_doc.save(output_path)

# ---------- PDF Processing ----------
def process_pdf(input_path, output_path):
    new_doc = Document()
    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                for block in text.split('\n\n'):
                    clean = block.replace('\n', ' ').strip()
                    if clean:
                        # Original English
                        new_doc.add_paragraph(clean)
                        # Arabic translation
                        ar = translate_text(clean)
                        ar_para = new_doc.add_paragraph(ar)
                        ar_para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                        new_doc.add_paragraph('')
    new_doc.save(output_path)

# ---------- Handlers ----------
@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.reply_to(
        message,
        "مرحباً! 👋\n\n"
        "أنا بوت الترجمة الأكاديمية العلمية.\n"
        "أرسل لي ملف *PDF* أو *DOCX* باللغة الإنجليزية،\n"
        "وسأرسل لك ملف Word يحتوي على:\n"
        "• النص الإنجليزي الأصلي\n"
        "• الترجمة العربية أسفله مباشرة ✅",
        parse_mode='Markdown'
    )

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    file_name = message.document.file_name
    file_ext = os.path.splitext(file_name)[1].lower()

    if file_ext not in ['.pdf', '.docx']:
        bot.reply_to(message, "⚠️ الملف غير مدعوم. يرجى إرسال ملف PDF أو DOCX فقط.")
        return

    bot.reply_to(message, "⚡ جاري المعالجة والترجمة... يرجى الانتظار.")

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        tmp_input = f"in_{message.chat.id}{file_ext}"
        tmp_output = f"out_{message.chat.id}.docx"

        with open(tmp_input, 'wb') as f:
            f.write(downloaded_file)

        if file_ext == '.docx':
            process_docx(tmp_input, tmp_output)
        elif file_ext == '.pdf':
            process_pdf(tmp_input, tmp_output)

        with open(tmp_output, 'rb') as f:
            bot.send_document(
                message.chat.id, f,
                caption="✅ تمت الترجمة بنجاح!"
            )

        os.remove(tmp_input)
        os.remove(tmp_output)

    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {str(e)}")
        print(f"[Error]: {e}")

# ---------- Start ----------
if __name__ == '__main__':
    print("✅ Bot is running...")
    bot.infinity_polling()
