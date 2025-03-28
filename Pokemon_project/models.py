from peewee import *

db = SqliteDatabase('data/pokemon.db')

class Pokemon(Model):
    name = CharField()
    type_1 = CharField()
    type_2 = CharField(null=True)
    total = IntegerField()
    hp = IntegerField()
    attack = IntegerField()
    defense = IntegerField()
    sp_atk = IntegerField()
    sp_def = IntegerField()
    speed = IntegerField()
    generation = IntegerField()
    legendary = BooleanField()

    class Meta:
        database = db

db.connect()
db.create_tables([Pokemon], safe=True)
