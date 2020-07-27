# -*- coding: utf-8 -*-

from subprocess import call
from pathlib import Path
from os import remove

from model import Person, Audio


def add_audio_to_db(user_id: int, path_to_audio: str):
    """Добавление аудиофайла на диск и в БД, предварительно его перегодировав
    Функция по пути path_to_audio находит файл и конвертирует его в .wav, сохраняет путь до нового файла в БД"""
    try:
        person = Person.get_or_create(id=user_id)
        count_audio = Audio.select().where(
            Audio.owner == person[0]).count()  # Считаем сколько уже файлов есть у пользователя

        # Вызываем функцию, которая конвертирует наш файл и вернёт путь до нового файла
        path_to_converted_audio = oga_to_wav(user_id, path_to_audio, count_audio, remove_old_file=True)
        if path_to_converted_audio:
            Audio.create(audio_path=path_to_converted_audio, owner=person[0])  # Сохраняем путь к файлу в БД
    except Exception:
        raise


def del_audio(user_id: int) -> None:
    """Удаление аудиофайлов из БД и диска"""
    person = Person.get_or_create(id=user_id)
    audio_files = Audio.select().where(Audio.owner == person[0])
    for audio in audio_files:
        remove(audio.audio_path)  # Удаляем файл из дериктории
        audio.delete_instance()  # Чистим запись в БД


def get_saved_audio(user_id: int):
    """Поиск в БД аудиофайлов пользователя по его id"""
    person = Person.get_or_create(id=user_id)
    audio = Audio.select().where(Audio.owner == person[0])
    return audio


def oga_to_wav(user_id: int, path_to_audio: str, n_file: int, remove_old_file: bool = True) -> str:
    try:
        #  Создадим директорию для хранения аудиофайлов
        input_path = Path.cwd() / path_to_audio
        output_path = Path.cwd() / "audio" / str(user_id)
        output_path.mkdir(parents=True, exist_ok=True)

        output = str(output_path / f'audio_message_{n_file}.wav')  # Задаём имя нового файла

        command = f"ffmpeg -i {str(input_path)} -vn -ar 16000 -ac 2 -f wav {output}"  # Команда конвертирования аудио
        call(command, shell=True)  # Вызываем системную команду
        if remove_old_file:
            remove(str(input_path))  # Удаляем старый файл
        return output
    except Exception:
        raise
