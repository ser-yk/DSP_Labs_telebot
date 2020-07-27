# -*- coding: utf-8 -*-

from os import remove
from pathlib import Path

import cv2

from model import Person, Photo


def find_face(path_to_photo: str) -> int:
    """Ищет лица на фотографии, возвращает число найденных лиц"""
    path_face_cascade = Path.cwd() / "data" / "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(str(path_face_cascade))

    image = cv2.imread(path_to_photo)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=7,
        minSize=(10, 10)
    )
    faces_detected = len(faces)
    # print("Лиц обнаружено: ", faces_detected)
    return faces_detected


def add_img_to_db(user_id: int, path_to_img: str) -> None:
    """Добавление фотографии в БД"""
    person = Person.get_or_create(id=user_id)
    Photo.create(photo_path=path_to_img, owner=person[0])


def get_saved_photo(user_id: int, limit: int = 10):
    """Поиск в БД фотографий пользователя по его id"""
    person = Person.get_or_create(id=user_id)
    photo = Photo.select().where(Photo.owner == person[0]).limit(limit)
    return photo


def del_photo(user_id: int) -> None:
    """Удаление фото из БД и диска"""
    person = Person.get_or_create(id=user_id)
    photos = Photo.select().where(Photo.owner == person[0])
    for photo in photos:
        remove(photo.photo_path)  # Удаляем файл из дериктории
        photo.delete_instance()  # Чистим запись в БД

