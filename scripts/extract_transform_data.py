import pandas as pd 


#Učitavanje podataka u pandas dataframeove
fifa21 = pd.read_csv('data/FIFA21_official_data.csv')
fifa22 = pd.read_csv('data/FIFA22_official_data.csv')

#Uklanjanje leading i trailing whitespaceova iz naziva stupaca i vrijednosti tablica
#Za vrijednosti tablica korišten regex zbog jednostavnosti i jer je strip() funkcija bila problematična
fifa21.columns = fifa21.columns.str.strip()
fifa22.columns = fifa22.columns.str.strip()
fifa21 = fifa21.replace(r'^\s+|\s+$', '', regex=True)
fifa22 = fifa22.replace(r'^\s+|\s+$', '', regex=True)

#Dodavanje stupca godine u dataframeove
fifa21["year"] = 2021
fifa22["year"] = 2022

#Spajanje dataframeova u jedan
dataset = pd.concat([fifa21, fifa22], ignore_index=True)
df = dataset


#Stvaranje novog stupca koji sadrži ime igrača bez brojeva, jer su neki igrači imali brojeve u imenu
df["Clean_Name"] = df["Name"].str.extract(r'(\D+)', expand=False)

#Grupiramo podatke prema ID-u i tražimo sve ID-ove koji imaju različite vrijednosti za Nacionality
#Uspoređuju se države za svakog igrača u 2021. i 2022. godini jer su u ulaznom datasetu neke države imale različite nazive
inconsistent_rows = df.groupby('ID')['Nationality'].nunique() > 1
inconsistent_ids = inconsistent_rows[inconsistent_rows == True].index

#Za svakog igrača kojemu su imena države različita u 2021. i 2022. godini, uzimamo ime države iz 2022. godine i postavljamo ga u 2021. godinu radi konzistentnosti 
for id in inconsistent_ids:
    country_2022 = df[(df['ID'] == id) & (df['year'] == 2022)]['Nationality'].values

    df.loc[(df['ID'] == id) & (df['year'] == 2021), 'Nationality'] = country_2022[0]

#Slično kao i za nacionalnost, provjeravamo sve igrače koji imaju različite linkove za državnu zastavu i uzimamo link iz 2022. godine
inconsistent_rows = df.groupby('ID')['Flag'].nunique() > 1

inconsistent_ids = inconsistent_rows[inconsistent_rows].index

for id in inconsistent_ids:
    flag_2022 = df[(df['ID'] == id) & (df['year'] == 2022)]['Flag'].values

    df.loc[(df['ID'] == id) & (df['year'] == 2021), 'Flag'] = flag_2022[0]

#Na sličan način provjeravamo sve igrače koji su obe godine u istom klubu, a imaju različite linkove za logo kluba
#Uzimamo link iz 2022. godine
inconsistent_rows = df.groupby('ID')['Club Logo'].nunique() > 1

inconsistent_ids = inconsistent_rows[inconsistent_rows].index

for id in inconsistent_ids:
    club2022 = df[(df['ID'] == id) & (df['year'] == 2022)]['Club'].values
    club2021 = df[(df['ID'] == id) & (df['year'] == 2021)]['Club'].values
    if club2022 == club2021:

        clublogo_2022 = df[(df['ID'] == id) & (df['year'] == 2022)]['Club Logo'].values

        df.loc[(df['ID'] == id) & (df['year'] == 2021), 'Club Logo'] = clublogo_2022[0]

#Brisanje linkova na logo kluba kod igrača koji nemaju klub
#Locira sve redove gdje je naziv kluba prazan i postavlja link na logo kluba na None
df.loc[df['Club'] == '', 'Club Logo'] = None

#Neki od linkova na logo kluba su bili u krivom formatu te nisu radili
#Regex ih popravlja u točni format https://cdn.sofifa.com/teams/{team_id}/{img_id}.png
df['Club Logo'] = df['Club Logo'].str.replace(r'https://cdn.sofifa.com/teams/(\d+)/\D+(\d+).png', r'https://cdn.sofifa.com/teams/\1/\2.png', regex=True)

#Pretvaranje stupca sa plaćama u obični broj koji je lakše obraditi uklanjanjem oznaka '€', 'M' i 'K'
wage_euro = []
for wage in df['Wage']:
    if pd.isna(wage): 
        wage_euro.append(None)
        continue
    wage_clean = wage.replace('€', '').replace('M', '').replace('K', '')
    if 'M' in wage:
        wage_euro.append((float(wage_clean) * 1000000))  
    elif 'K' in wage:
        wage_euro.append((float(wage_clean) * 1000))  
    else:
        wage_euro.append((float(wage_clean)))

df['Wage_euro'] = wage_euro

#Na isti način pretvaramo i vrijednost igrača u obični broj
value_euro = []
for value in df['Value']:
    if pd.isna(value): 
        value_euro.append(None)
        continue
    value_clean = value.replace('€', '').replace('M', '').replace('K', '')
    if 'M' in value:
        value_euro.append((float(value_clean) * 1000000))  
    elif 'K' in value:
        value_euro.append((float(value_clean) * 1000))  
    else:
        value_euro.append((float(value_clean)))

df['Value_euro'] = value_euro

#Na isti način pretvaramo i klauzulu igrača u obični broj
release_euro = []
for release in df['Release Clause']:
    if pd.isna(release): 
        release_euro.append(None)
        continue
    release_clean = release.replace('€', '').replace('M', '').replace('K', '')
    if 'M' in release:
        release_euro.append((float(release_clean) * 1000000))  
    elif 'K' in release:
        release_euro.append((float(release_clean) * 1000))  
    else:
        release_euro.append((float(release_clean)))

df['Release Clause_euro'] = release_euro


#Razdvajanje stupca Work Rate u dva nova stupca - Attack Work Rate i Defense Work Rate za lakšu upotrebu i razumljivost
df[['Attack Work Rate', 'Defense Work Rate']] = df['Work Rate'].str.split('/ ', expand=True)


#Razdvajanje stupca Body Type u dva nova stupca - Body Type Only i Height Range
#Body Type Only sadrži samo tip tijela, a Height Range raspon visine
df[['Body Type Only', 'Height Range']] = df['Body Type'].str.split('(', expand=True)
df['Height Range'] = df['Height Range'].str.rstrip(')')


#Brisanje body typeova koji se javljaju samo jednom
values = df['Body Type Only'].value_counts()
df = df[df['Body Type Only'].isin(values[values > 1].index)]
df['Body Type Only'].value_counts()

#Razdvajanje stupca Height Range na lower i upper bound za lakšu uporabu
df[['Height Range Lower Bound', 'Height Range Upper Bound']] = (
    df['Height Range'].str.split(r'[+-]', expand=True)
)

#Ako raspon visine ima samo gornju granicu (npr. 180-) tada će zbog prijasnjeg razdvajanja lower bound biti 180, a upper bound None
#Da to popravimo, uzimamo sve redove gdje je height range takvog oblika i postavljamo lower bound na None, a upper bound na gornju granicu
#Suprotni slučaj gdje imamo samo donju granicu (npr. 180+) je automatski pokriven u gornjem dijelu koda
mask = df['Height Range'].notna() & df['Height Range'].str.endswith('-')
df.loc[mask, 'Height Range Upper Bound'] = df.loc[mask, 'Height Range Lower Bound']
df.loc[mask, 'Height Range Lower Bound'] = None

#Vrijednosti nekih pozicija u tablici imale su html tagove pa ih je potrebno očistiti
#Regex ignorira sve što je između < > i vraća samo ono što dolazi iza
df['Position Clean'] = df['Position'].str.extract(r'<.*>(\w*)')

#Pretvaranje u datetime format
df['Joined'] = pd.to_datetime(df['Joined'])

#Neki klubovi u Loaned From stupcu su bili unutar html tagova pa treba izvući samo ime kluba
#Regex ignorira html tagove <tag> i </tag> i vraća samo ono što se nalazi između
df['Loaned From Club'] = df['Loaned From'].str.extract(r'<[^\<]*>([^\<]*)<[^\<]*>')

#Uzima samo vrijednost godine iz Contract Valid Until stupca jer su neke vrijednosti bile samo godine, a neke točan datum
df['Contract Valid Until Year'] = df['Contract Valid Until'].str.extract(r'(\d{4})')


#Stupci za visinu i težinu su između godina bili u različitim mjernim jedinicama te su bili stringovi oblika vrijednost + mjerna jedinica (npr. 180cm, 6'2", 70kg, 154lbs)
#Pretvaramo ih u obične brojeve i sve jedinice pretvaramo u metricki sustav
def feet_to_cm(height):
    if 'cm' in height:
        return int(height.replace('cm', ''))
    elif "'" in height:
        parts = height.split("'")
        feet = int(parts[0]) 
        if len(parts) > 1:
            inches = int(parts[1])
        else:
            inches = 0 
        return int(feet * 30.48 + inches * 2.54)
    return None

df['Height_cm'] = df['Height'].apply(feet_to_cm)
df[['year', 'Height_cm']]

def lbs_to_kg(weight):
    if 'kg' in weight:
        return int(weight.replace('kg', ''))
    elif "lbs" in weight:
        weight_lbs = int(weight.replace('lbs', '')) 
        return int(weight_lbs * 0.453)
    return None

df['Weight_kg'] = df['Weight'].apply(lbs_to_kg)
df[['year', 'Weight_kg']]

#Na sličan način kao i ranije u skripti, provjeravamo igrače kojima se visina razlikuje te uzimamo visinu iz 2022. godine
#Pretpostavka da igrači ne rastu
inconsistent_rows = df.groupby('ID')['Height_cm'].nunique() > 1

inconsistent_ids = inconsistent_rows[inconsistent_rows].index

for id in inconsistent_ids:
    height_2022 = df[(df['ID'] == id) & (df['year'] == 2022)]['Height_cm'].values

    df.loc[(df['ID'] == id) & (df['year'] == 2021), 'Height_cm'] = height_2022[0]
    

#Na sličan način provjeravamo konzistentnost preferirane noge
#Pretpostavka da je noga s kojom igrač najbolje igra uvijek ista
inconsistent_rows = df.groupby('ID')['Preferred Foot'].nunique() > 1

inconsistent_ids = inconsistent_rows[inconsistent_rows].index

for id in inconsistent_ids:
    foot_2022 = df[(df['ID'] == id) & (df['year'] == 2022)]['Preferred Foot'].values

    df.loc[(df['ID'] == id) & (df['year'] == 2021), 'Preferred Foot'] = foot_2022[0]

#Provjera konzistentnosti tipova tijela igrača - uzimamo tip tijela iz 2022. godine
inconsistent_rows = df.groupby('ID')['Body Type Only'].nunique() > 1

inconsistent_ids = inconsistent_rows[inconsistent_rows].index

for id in inconsistent_ids:
    body_2022 = df[(df['ID'] == id) & (df['year'] == 2022)]['Body Type Only'].values

    df.loc[(df['ID'] == id) & (df['year'] == 2021), 'Body Type Only'] = body_2022[0]
    
#Vrijednost Real Face pretvaramao u bool umjesto Yes/No radi lakše uporabe
df.loc[:,'Real Face'] = df['Real Face'].replace({'Yes': True, 'No': False}).astype(bool)
df[['Real Face', 'ID']].head()


#Odabir finalnih čistih stupaca
columns = ['ID', 'Clean_Name', 'year', 'Age', 'Photo', 'Nationality', 'Flag', 'Overall',
       'Potential', 'Club', 'Club Logo', 'Value_euro', 'Wage_euro', 'Special',
       'Preferred Foot', 'International Reputation', 'Weak Foot',
       'Skill Moves', 'Attack Work Rate', 'Defense Work Rate', 'Body Type Only','Height Range', 'Height Range Lower Bound', 'Height Range Upper Bound',
         'Real Face','Position Clean',
       'Jersey Number', 'Joined', 'Loaned From Club', 'Contract Valid Until Year',
       'Height_cm', 'Weight_kg', 'Crossing', 'Finishing', 'HeadingAccuracy',
       'ShortPassing', 'Volleys', 'Dribbling', 'Curve', 'FKAccuracy',
       'LongPassing', 'BallControl', 'Acceleration', 'SprintSpeed', 'Agility',
       'Reactions', 'Balance', 'ShotPower', 'Jumping', 'Stamina', 'Strength',
       'LongShots', 'Aggression', 'Interceptions', 'Positioning', 'Vision',
       'Penalties', 'Composure', 'Marking', 'StandingTackle', 'SlidingTackle',
       'GKDiving', 'GKHandling', 'GKKicking', 'GKPositioning', 'GKReflexes',
       'Best Position', 'Best Overall Rating', 'Release Clause_euro',
       'DefensiveAwareness']

df_clean = df[columns]

#Preimenovanje stupaca
df_clean.columns = ['ID', 'Name', 'Year', 'Age', 'Photo', 'Nationality', 'Flag', 'Overall',
       'Potential', 'Club', 'Club Logo', 'Value_Euro', 'Wage_Euro', 'Special',
       'Preferred Foot', 'International Reputation', 'Weak Foot',
       'Skill Moves', 'Attack Work Rate', 'Defense Work Rate', 'Body Type','Height Range', 'Height Range Lower Bound', 'Height Range Upper Bound',
         'Real Face','Position',
       'Jersey Number', 'Joined', 'Loaned From', 'Contract Valid Until',
       'Height_cm', 'Weight_kg', 'Crossing', 'Finishing', 'HeadingAccuracy',
       'ShortPassing', 'Volleys', 'Dribbling', 'Curve', 'FKAccuracy',
       'LongPassing', 'BallControl', 'Acceleration', 'SprintSpeed', 'Agility',
       'Reactions', 'Balance', 'ShotPower', 'Jumping', 'Stamina', 'Strength',
       'LongShots', 'Aggression', 'Interceptions', 'Positioning', 'Vision',
       'Penalties', 'Composure', 'Marking', 'StandingTackle', 'SlidingTackle',
       'GKDiving', 'GKHandling', 'GKKicking', 'GKPositioning', 'GKReflexes',
       'Best Position', 'Best Overall Rating', 'Release Clause_Euro',
       'DefensiveAwareness']


#Preimenovanje stupaca i popravljanje tipova radi rješavanja problema s bazom podataka
df_clean = df_clean.copy()
df_clean.rename(columns={"ID": "PlayerID"}, inplace=True)
df_clean.rename(columns={"Club": "ClubName"}, inplace=True)

df_clean.columns = df_clean.columns.str.replace(' ', '')
df_clean.columns = df_clean.columns.str.lower()
df_clean['jerseynumber'] = pd.to_numeric(df_clean['jerseynumber'], errors='coerce').astype('Int64')

#Spremanje čistih podataka u csv datoteku
df_clean.to_csv('data/clean_data.csv', index=False)