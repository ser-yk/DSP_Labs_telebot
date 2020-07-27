# -*- coding: utf-8 -*-

from os import remove
from pathlib import Path

import telebot

from processing.photo import find_face, add_img_to_db, get_saved_photo, del_photo
from processing.audio import add_audio_to_db, get_saved_audio, del_audio

bot = telebot.TeleBot(r'')


# Начало работы, отправка приветствия
@bot.message_handler(commands=['start'])
def handle_message(message):
    """Функция ждёт команды 'start', после получения которой отсылает приветственное сообщение"""
    print(message.text)
    bot.send_message(chat_id=message.chat.id,
                     text='Привет! \nЯ умею сохранять голосовые сообщения и фото, на которых есть лица. '
                          'Просто отправте фотографию или голосовое сообщение. Для просмотра комманд введите /')


# Добавить фото в БД
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """Функция отлавливает все сходящие фотографии и сохраняет в на диск фото, добавляя ссылку на него в БД"""
    try:
        # Сохраняем полученное фото из сообщения
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        path_to_img = './' + file_info.file_path
        with open(path_to_img, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Проверяем есть ли на фото лица
        if find_face(path_to_img):
            add_img_to_db(message.from_user.id, path_to_img)  # Сохраняем фото с лицами
            bot.send_message(chat_id=message.chat.id, text='На фото есть лица. Фото сохранено')
        else:
            remove(path_to_img)  # Удаляем фото, т.к. лица не были обнаружены
            bot.send_message(chat_id=message.chat.id, text='На фото нет лиц. Фото не сохранено')

    except Exception as e:
        bot.reply_to(message, 'Не удалось сохранить фото. Неизвестная ошибка')


# Добавить аудиозапись в БД
@bot.message_handler(content_types=['voice'])
def handle_audio(message):
    """Функция отлавливает все сходящие голосовые сообщения и сохраняет их предварительно конвертируя их в .wav
     Аудиофайл сохраняется на диске, ссылка на него добавляется в БД"""
    try:
        # Сохраняем полученную в сообщении аудиозапись
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        path_to_audio = './' + file_info.file_path
        with open(path_to_audio, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Конвертирует аудиофайл и сохраняем в БД
        add_audio_to_db(message.from_user.id, path_to_audio)

        bot.send_message(chat_id=message.chat.id, text='Я сохранил аудиозапись')
    except Exception as e:
        bot.reply_to(message, 'Не удалось сохранить аудиозапись. Неизвестная ошибка')


# Вывод сохранённых фото
@bot.message_handler(commands=['get_photo'])
def list_photo(message):
    """Функция по запросу пользователя отправляет ему фото, сохранённые в БД"""
    try:
        photos = get_saved_photo(message.from_user.id)  # Получаем фото из БД
        cnt = 1
        # Если фото есть, проходимся по ним и отправляем их по одному в сообщении
        if photos.count() > 0:
            for photo in photos:
                with open(photo.photo_path, 'rb') as img:
                    bot.send_photo(chat_id=message.chat.id, photo=img, caption=f'Фотография №{cnt}')
                cnt += 1
        else:
            bot.send_message(chat_id=message.chat.id, text='У Вас нет сохранённых фото')
    except Exception as e:
        bot.reply_to(message, 'Не удалось получить фото. Неизвестная ошибка')


# Вывод сохранённых аудиозаписей
@bot.message_handler(commands=['get_audio'])
def list_audio(message):
    """Функция по запросу пользователя отправляет ему в сообщении аудиофайлы, сохранённые в БД"""
    try:
        audio = get_saved_audio(message.from_user.id)  # Получаем аудиофайлы из БД
        if audio.count() > 0:  # Если есть что отправить пользователю, отправляем по одному.
            for i in audio:
                with open(i.audio_path, 'rb') as audio_file:
                    bot.send_audio(chat_id=message.chat.id, audio=audio_file)
        else:
            bot.send_message(chat_id=message.chat.id, text='У Вас нет сохранённых аудиозаписей')
    except Exception as e:
        bot.reply_to(message, 'Не удалось получить аудиозаписи. Неизвестная ошибка')


# Удаление фото
@bot.message_handler(commands=['del_photo'])
def reset_photo(message):
    """Функция по требованию пользователя удаляет все его сохранённые фотографии"""
    try:
        del_photo(message.from_user.id)
        bot.send_message(chat_id=message.chat.id, text=f'Все фотографии были удалены')
    except Exception as e:
        bot.reply_to(message, 'Не удалось удалить фото. Неизвестная ошибка')


# Удаление аудиозаписей
@bot.message_handler(commands=['del_audio'])
def reset_audio(message):
    """Функция по требованию пользователя удаляет все его сохранённые аудиофайлы"""
    try:
        del_audio(message.from_user.id)
        bot.send_message(chat_id=message.chat.id, text=f'Все аудиозаписи были удалены')
    except Exception as e:
        bot.reply_to(message, 'Не удалось удалить аудиозаписи. Неизвестная ошибка')


if __name__ == '__main__':
    # Создадим директории, в которых будут храниться полученные фото и голосовые сообщения
    voice_path = Path.cwd() / "voice"
    voice_path.mkdir(parents=True, exist_ok=True)
    photos_path = Path.cwd() / "photos"
    photos_path.mkdir(parents=True, exist_ok=True)

    while True:
        bot.polling(none_stop=True, timeout=10)
