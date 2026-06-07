import os
import threading
import requests
import google.generativeai as genai
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 1. הגדרת שרת Flask כדי ש-Render לא יכניס את הבוט לשינה
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app_flask.run(host='0.0.0.0', port=10000)

# 2. הגדרת Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. פונקציית התגובה להודעות
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        response = model.generate_content(text)
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("מצטער, הייתה שגיאה בחיבור ל-Gemini.")

# 4. הרצה ראשית
if __name__ == '__main__':
    # הפעלת שרת ה-Flask ברקע
    threading.Thread(target=run_flask).start()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # פקודת ניקוי: מוחקת הגדרות עבר מטלגרם כדי למנוע Conflict
    requests.get(f"https://api.telegram.org/bot{token}/deleteWebhook?drop_pending_updates=True")
    
    # בניית הבוט והרצתו
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply))
    
    print("Bot is ready and polling...")
    app.run_polling()
