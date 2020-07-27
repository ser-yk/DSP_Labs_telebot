from peewee import *


db = SqliteDatabase('data.db')


class Person(Model):
    id = IntegerField(primary_key=True)

    class Meta:
        database = db


class Photo(Model):
    photo_path = CharField()
    owner = ForeignKeyField(Person, related_name='photo')

    class Meta:
        database = db


class Audio(Model):
    audio_path = CharField()
    owner = ForeignKeyField(Person, related_name='audio')

    class Meta:
        database = db


if __name__ == '__main__':
    Person.create_table()
    Photo.create_table()
    Audio.create_table()

