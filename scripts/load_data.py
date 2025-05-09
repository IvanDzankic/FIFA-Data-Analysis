import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import os
from dotenv import load_dotenv
import psycopg2

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


engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')


# Run database creation script
with open('scripts/db_creation.sql', 'r') as file:
    sql_script = file.read()

sql_commands = sql_script.split(';')


with psycopg2.connect(**config) as conn:
    with conn.cursor() as cur:
        for command in sql_commands:
            command = command.strip()
            if command:
                try:
                    cur.execute(command)
                except Exception as e:
                    print("Skipped command: ", e)



csv = "data/clean_data.csv"
df = pd.read_csv(csv, low_memory=False)

df.columns = df.columns.str.strip()
df = df.replace(r'^\s+|\s+$', '', regex=True)
df = df.replace('', np.nan)


#Create staging table
df.to_sql('stagingfifa', con=engine, if_exists='replace', index=False)


#Create dimension tables
dim_club = df[['clubname', 'clublogo']].drop_duplicates().dropna()
dim_year = df[['year']].drop_duplicates().dropna()
dim_player = df[['playerid', 'name', 'photo', 'nationality', 'flag', 'preferredfoot', 'bodytype', 'heightrange', 'heightrangelowerbound', 'heightrangeupperbound', 'height_cm', 'realface']].drop_duplicates(subset=['playerid'])
dim_position = df[['position']].drop_duplicates().dropna()

workrate = pd.concat([df['attackworkrate'], df['defenseworkrate']]).drop_duplicates().dropna().reset_index(drop=True)
dim_workrate = pd.DataFrame(workrate, columns=['workratevalue'])


dim_club.to_sql('dimclub', engine, if_exists='append', index=False)
dim_year.to_sql('dimyear', engine, if_exists='append', index=False)
dim_player.to_sql('dimplayer', engine, if_exists='append', index=False)
dim_position.to_sql('dimposition', engine, if_exists='append', index=False)
dim_workrate.to_sql('dimworkrate', engine, if_exists='append', index=False)


# Read DimClub
club_mapping = pd.read_sql("SELECT clubid, clubname FROM dimclub", engine)

# Read DimPosition
position_mapping = pd.read_sql("SELECT positionid, position FROM dimposition", engine)

# Read DimWorkRate
workrate_mapping = pd.read_sql("SELECT workrateid, workratevalue FROM dimworkrate", engine)

# Read DimYear
year_mapping = pd.read_sql("SELECT yearid, year FROM dimyear", engine)



# Map ClubID
df = df.merge(club_mapping, on='clubname', how='left')

df = df.merge(club_mapping.rename(columns={'clubid': 'loanedfromid'}), 
              left_on='loanedfrom', right_on='clubname', how='left')

# Map PositionID (za Position i BestPosition) 
df = df.merge(position_mapping.rename(columns={'positionid': 'positionid'}), 
              left_on='position', right_on='position', how='left')

df = df.merge(position_mapping.rename(columns={'positionid': 'bestpositionid'}), 
              left_on='bestposition', right_on='position', how='left')

# Map WorkRateID (za AttackWorkRate i DefenseWorkRate)
df = df.merge(workrate_mapping.rename(columns={'workrateid': 'attackworkrateid'}), 
              left_on='attackworkrate', right_on='workratevalue', how='left')

df = df.merge(workrate_mapping.rename(columns={'workrateid': 'defenseworkrateid'}), 
              left_on='defenseworkrate', right_on='workratevalue', how='left')

# Map YearID
df = df.merge(year_mapping, on='year', how='left')


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

fact_player_stats.to_sql('factplayerstats', engine, if_exists='append', index=False)