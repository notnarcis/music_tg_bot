import logging
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Вставьте сюда свой токен, который дали через BotFather
TOKEN = '8303819401:AAFvK8_JxNGpm5hrwm5DPyrhXgaj0iUaWbY'
AUDIO_API_KEY = '8dd8cb2731915be1a92d84798f19f96f'  # API ключ для Audd.io или другого сервиса

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Функция для обработки команды start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Отправь мне аудиофайл, и я определю песню!')


# Функция для обработки аудиофайлов
def handle_audio(update: Update, context: CallbackContext) -> None:
    audio_file = update.message.audio
    file_id = audio_file.file_id
    new_file = context.bot.get_file(file_id)

    # Скачиваем аудиофайл
    audio_file_path = new_file.download()

    # Отправляем аудиофайл на сервис распознавания
    result = recognize_music(audio_file_path)

    if result:
        song_info = f"Название: {result['title']}\nИсполнитель: {result['artist']}"
    else:
        song_info = "Не удалось распознать песню."

    # Отправляем результат пользователю
    update.message.reply_text(song_info)


# Функция для обращения к API распознавания музыки
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


# Главная функция для запуска бота
def main():
    # Создаем Updater и Dispatcher
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Обработчики команд и сообщений
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.audio, handle_audio))

    # Запуск бота
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
