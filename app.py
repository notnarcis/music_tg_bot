from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import logging
import requests

TOKEN = '8303819401:AAFvK8_JxNGpm5hrwm5DPyrhXgaj0iUaWbY'

AUDIO_API_KEY = '8dd8cb2731915be1a92d84798f19f96f'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Отправь мне аудиофайл, и я определю песню!')

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_file = update.message.audio
    new_file = await context.bot.get_file(audio_file.file_id)
    audio_file_path = await new_file.download_to_drive()
    
    result = recognize_music(audio_file_path)
    if result:
        song_info = f"Название: {result['title']}\nИсполнитель: {result['artist']}"
    else:
        song_info = "Не удалось распознать песню."
    
    await update.message.reply_text(song_info)

def recognize_music(audio_file_path: str) -> dict:
    url = 'https://api.audd.io/'
    params = {
        'api_token': AUDIO_API_KEY,
        'file': open(audio_file_path, 'rb'),
        'return': 'song,artist'
    }
    response = requests.post(url, files=params)
    data = response.json()
    if data.get('status') == 'success':
        song = data.get('result')
        return {'title': song['title'], 'artist': song['artist']}
    return None

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    app.run_polling()

if __name__ == "__main__":
    main()
