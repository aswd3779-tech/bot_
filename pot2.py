import os
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp
import nest_asyncio
import asyncio

# يقرأ التوكن من البيئة (من السيرفر)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TEMP_DIR = "temp_videos"

# إنشاء مجلد مؤقت
os.makedirs(TEMP_DIR, exist_ok=True)

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
    "geo_bypass": True,          # يتجاوز القيود الجغرافية
    "nocheckcertificate": True,  # يتجاهل مشاكل SSL
    "ignoreerrors": True,        # يتخطى الأخطاء المؤقتة
}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        await msg.reply_video(video=open(file_path, "rb"), caption="✅ تم تحميل الفيديو!")

    except Exception as e:
        await msg.reply_text(f"❌ فشل تحميل الفيديو:\n{e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

async def main():
    if not BOT_TOKEN:
        print("⚠ لم يتم العثور على التوكن! تأكد من إضافته في إعدادات Render.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت يعمل الآن...")
    await app.run_polling()

if __name__ == "__main__":
    # تشغيل Flask و Ping ذاتي لإبقاء السيرفر حي
    from flask import Flask
    import threading, time, requests, os, asyncio

    app_flask = Flask(_name_)

    @app_flask.route('/')
    def home():
        return "✅ Bot is alive!"

    def keep_alive():
        def run():
            app_flask.run(host="0.0.0.0", port=10000)
        t = threading.Thread(target=run)
        t.start()

    def self_ping():
        while True:
            try:
                url = os.environ.get("RENDER_EXTERNAL_URL")
                if url:
                    requests.get(url)
            except:
                pass
            time.sleep(240)  # كل 4 دقائق

    keep_alive()
    threading.Thread(target=self_ping, daemon=True).start()

    asyncio.get_event_loop().run_until_complete(main())

