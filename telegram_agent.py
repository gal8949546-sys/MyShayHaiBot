import os
import threading
from flask import Flask
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# הגדרת המפתחות מהסביבה
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# הגדרת Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# שרת Flask קטן כדי ש-Render לא יסגור את הבוט
server = Flask(__name__)
@server.route('/')
def home():
    return "Bot is running!"

def run_server():
    server.run(host='0.0.0.0', port=10000)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("מצטער, הייתה שגיאה בחיבור ל-Gemini.")

if __name__ == '__main__':
    # מפעילים את השרת ברקע
    threading.Thread(target=run_server).start()
    
    # מפעילים את הבוט
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot Started")
    app.run_polling()