import os
import google.generativeai as genai
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram import Update
import threading
from flask import Flask

# הגדרת שרת Flask כדי ש-Render לא יסגור את השירות
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "OK"
threading.Thread(target=lambda: app_flask.run(host='0.0.0.0', port=10000)).start()

# הגדרת הבוט
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        response = model.generate_content(text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("שגיאה בחיבור ל-Gemini")

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply))
    print("Bot is polling...")
    app.run_polling()