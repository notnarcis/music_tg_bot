from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import logging
import requests
import os

TOKEN = '8303819401:AAFvK8_JxNGpm5hrwm5DPyrhXgaj0iUaWbY'
AUDIO_API_KEY = '8dd8cb2731915be1a92d84798f19f96f'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Отправь мне аудиофайл, и я попробую определить песню!')

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_file = update.message.audio
    if not audio_file:
        await update.message.reply_text("Пожалуйста, отправьте аудиофайл.")
        return

    # Скачиваем файл на диск
    new_file = await context.bot.get_file(audio_file.file_id)
    audio_file_path = await new_file.download_to_drive()

    logger.info(f"Файл скачан: {audio_file_path}")

    # Распознаём музыку
    result = recognize_music(audio_file_path)

    # Удаляем временный файл после распознавания
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)
        logger.info(f"Временный файл удалён: {audio_file_path}")

    if result:
        song_info = f"Название: {result['title']}\nИсполнитель: {result['artist']}"
    else:
        song_info = "Не удалось распознать песню."

    await update.message.reply_text(song_info)

def recognize_music(audio_file_path: str) -> dict:
    url = 'https://api.audd.io/'
    try:
        with open(audio_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'api_token': AUDIO_API_KEY,
                'return': 'song,artist'
            }
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            data = response.json()

            if data.get('status') == 'success' and data.get('result'):
                song = data['result']
                return {'title': song.get('title', 'Неизвестно'), 'artist': song.get('artist', 'Неизвестно')}
    except Exception as e:
        logger.error(f"Ошибка при распознавании музыки: {e}")
    return None

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    app.run_polling()

if __name__ == "__main__":
    main()
