import os
import time
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp
import nest_asyncio
import asyncio

# قراءة التوكن من البيئة (من Render)
BOT_TOKEN = os.getenv("BOT_TOKEN")
TEMP_DIR = "temp_videos"
os.makedirs(TEMP_DIR, exist_ok=True)

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running successfully!"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return

    url = msg.text.strip()

    if not (url.startswith("http://") or url.startswith("https://")):
        await msg.reply_text("❌ هذا ليس رابط صالح.")
        return

    file_path = os.path.join(TEMP_DIR, f"{msg.from_user.id}_{int(time.time())}.mp4")

    await msg.reply_text("⏳ جاري تحميل الفيديو...")

    try:
       ydl_opts = {
    "outtmpl": file_path,
    "format": "mp4/best",
    "quiet": True,
    "noplaylist": True,
    "skip_download": False,
    "extract_flat": False,
    "geo_bypass": True,  # يتجاوز القيود الجغرافية
    "nocheckcertificate": True,  # يتجاهل مشاكل الشهادات
}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        await msg.reply_video(video=open(file_path, "rb"), caption="✅ تم تحميل الفيديو!")

    except Exception as e:
        await msg.reply_text(f"❌ فشل تحميل الفيديو:\n{e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

async def start_bot():
    print("✅ تشغيل البوت...")
    nest_asyncio.apply()
    app_builder = ApplicationBuilder().token(BOT_TOKEN).build()
    app_builder.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app_builder.run_polling()

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # تشغيل Flask في خيط مستقل
    threading.Thread(target=lambda: asyncio.run(start_bot()), daemon=True).start()
    run_flask()

