import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import os
from dotenv import load_dotenv
import psycopg2


#Učitanje parametara okruženja radi povezivanja na bazu podataka
load_dotenv()

db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

config = {
    "dbname": db_name,
    "user": db_user,
    "password": db_password,
    "host": db_host,
    "port": db_port,
}

# Kreiranje konekcije na bazu podataka pomoću SQLAlchemy pomoću koje se kasnije baza podataka puni
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')


# Učitaanje SQL skripte za kreiranje baze podataka
with open('scripts/db_creation.sql', 'r') as file:
    sql_script = file.read()

sql_commands = sql_script.split(';')

# Povezivanje na bazu podataka i izvršavanje SQL naredbi za kreaciju tablica
# Sličnu mogućnost imamo i u SQLAlchemy, ali je dolazilo do grešaka prilikom kreiranja tablica te se nisu svi atributi kreirali
# pa je korišten psycopg2 za konekciju i raw izvršavanje SQL naredbi iz skripte db_creation.sql
with psycopg2.connect(**config) as conn:
    with conn.cursor() as cur:
        for command in sql_commands:
            command = command.strip()
            if command:
                try:
                    cur.execute(command)
                except Exception as e:
                    print("Skipped command: ", e)


#Učitavanje CSV datoteke sa očišćenim podacima u dataframe
csv = "data/clean_data.csv"
df = pd.read_csv(csv, low_memory=False)

df.columns = df.columns.str.strip()
df = df.replace(r'^\s+|\s+$', '', regex=True)
df = df.replace('', np.nan)


#Punjenje staging tablice sa svim podacima iz CSV datoteke
df.to_sql('stagingfifa', con=engine, if_exists='replace', index=False)


#Kreiranje dataframeova koji sadrže podatke za svaku od dimenzijskih tablica
dim_club = df[['clubname', 'clublogo']].drop_duplicates().dropna()
dim_year = df[['year']].drop_duplicates().dropna()
dim_player = df[['playerid', 'name', 'photo', 'nationality', 'flag', 'preferredfoot', 'bodytype', 'heightrange', 'heightrangelowerbound', 'heightrangeupperbound', 'height_cm', 'realface']].drop_duplicates(subset=['playerid'])
dim_position = df[['position']].drop_duplicates().dropna()

workrate = pd.concat([df['attackworkrate'], df['defenseworkrate']]).drop_duplicates().dropna().reset_index(drop=True)
dim_workrate = pd.DataFrame(workrate, columns=['workratevalue'])

#Punjenje dimenzijskih tablica sa podacima koristeći SQLAlchemy
dim_club.to_sql('dimclub', engine, if_exists='append', index=False)
dim_year.to_sql('dimyear', engine, if_exists='append', index=False)
dim_player.to_sql('dimplayer', engine, if_exists='append', index=False)
dim_position.to_sql('dimposition', engine, if_exists='append', index=False)
dim_workrate.to_sql('dimworkrate', engine, if_exists='append', index=False)

#Sada je potrebno napuniti fact tablicu pomoću id-eva iz dimenzijskih tablica

#Učitavanje bitnih podataka iz dimenzijskih tablica za mapiranje na fact tablicu (id-evi i imena)
club_mapping = pd.read_sql("SELECT clubid, clubname FROM dimclub", engine)

position_mapping = pd.read_sql("SELECT positionid, position FROM dimposition", engine)

workrate_mapping = pd.read_sql("SELECT workrateid, workratevalue FROM dimworkrate", engine)

year_mapping = pd.read_sql("SELECT yearid, year FROM dimyear", engine)



# Spaja fact tablicu sa dimenzijskim tablicama po imenima, slično kao i kod SQL joinova te tako dobiva id-eve iz dimenzijskih tablica
# Sada u fact tablici imamo i imena i id-eve
df = df.merge(club_mapping, on='clubname', how='left')

df = df.merge(club_mapping.rename(columns={'clubid': 'loanedfromid'}), 
              left_on='loanedfrom', right_on='clubname', how='left')

df = df.merge(position_mapping.rename(columns={'positionid': 'positionid'}), 
              left_on='position', right_on='position', how='left')

df = df.merge(position_mapping.rename(columns={'positionid': 'bestpositionid'}), 
              left_on='bestposition', right_on='position', how='left')

df = df.merge(workrate_mapping.rename(columns={'workrateid': 'attackworkrateid'}), 
              left_on='attackworkrate', right_on='workratevalue', how='left')

df = df.merge(workrate_mapping.rename(columns={'workrateid': 'defenseworkrateid'}), 
              left_on='defenseworkrate', right_on='workratevalue', how='left')

df = df.merge(year_mapping, on='year', how='left')

# Za fact tablicu odabiremo samo id-eve i brojevne podatke, ostali podaci dobivaju se spajanjem sa dimenzijskim tablicama
fact_player_stats = df[[
    'yearid', 'playerid', 'clubid', 'positionid', 'bestpositionid', 
    'attackworkrateid', 'defenseworkrateid', 'loanedfromid', 'age', 'jerseynumber', 'overall', 
    'potential', 'value_euro', 'wage_euro', 'special', 'internationalreputation', 
    'weakfoot', 'skillmoves', 'joined', 'contractvaliduntil', 'weight_kg', 'crossing', 'finishing', 'headingaccuracy', 
    'shortpassing', 'volleys', 'dribbling', 'curve', 'fkaccuracy', 
    'longpassing', 'ballcontrol', 'acceleration', 'sprintspeed', 'agility', 
    'reactions', 'balance', 'shotpower', 'jumping', 'stamina', 'strength', 
    'longshots', 'aggression', 'interceptions', 'positioning', 'vision', 
    'penalties', 'composure', 'marking', 'standingtackle', 'slidingtackle', 
    'gkdiving', 'gkhandling', 'gkkicking', 'gkpositioning', 'gkreflexes', 
    'bestoverallrating', 'releaseclause_euro', 'defensiveawareness'
]]

# Punjenje fact tablice sa podacima 
fact_player_stats.to_sql('factplayerstats', engine, if_exists='append', index=False)