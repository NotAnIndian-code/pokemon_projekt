import pandas as pd
from models import Pokemon
from peewee import fn

def load_pokemon_data(file):
    df = pd.read_csv(file)
    
    for _, row in df.iterrows():
        Pokemon.create(
            name=row['Name'],
            type_1=row['Type 1'],
            type_2=row['Type 2'],
            total=row['Total'],
            hp=row['HP'],
            attack=row['Attack'],
            defense=row['Defense'],
            sp_atk=row['Sp. Atk'],
            sp_def=row['Sp. Def'],
            speed=row['Speed'],
            generation=row['Generation'],
            legendary=row['Legendary']
        )

def query_pokemon_data():
    return Pokemon.select()

def get_pokemon_stats():
    avg_hp = Pokemon.select(fn.AVG(Pokemon.hp)).scalar()
    avg_attack = Pokemon.select(fn.AVG(Pokemon.attack)).scalar()
    return {'avg_hp': avg_hp, 'avg_attack': avg_attack}