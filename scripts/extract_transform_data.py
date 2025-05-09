import pandas as pd 

fifa21 = pd.read_csv('data/FIFA21_official_data.csv')
fifa22 = pd.read_csv('data/FIFA22_official_data.csv')

fifa21.columns = fifa21.columns.str.strip()
fifa22.columns = fifa22.columns.str.strip()
fifa21 = fifa21.replace(r'^\s+|\s+$', '', regex=True)
fifa22 = fifa22.replace(r'^\s+|\s+$', '', regex=True)


fifa21["year"] = 2021
fifa22["year"] = 2022
dataset = pd.concat([fifa21, fifa22], ignore_index=True)
df = dataset


#Clean name
df["Clean_Name"] = df["Name"].str.extract(r'(\D+)', expand=False)

#Country name consistency
inconsistent_rows = df.groupby('ID')['Nationality'].nunique() > 1
inconsistent_ids = inconsistent_rows[inconsistent_rows == True].index

#Copy 2022 dataset country name to 2021
for id in inconsistent_ids:
    country_2022 = df[(df['ID'] == id) & (df['year'] == 2022)]['Nationality'].values

    df.loc[(df['ID'] == id) & (df['year'] == 2021), 'Nationality'] = country_2022[0]

#Flag link consistency
inconsistent_rows = df.groupby('ID')['Flag'].nunique() > 1

inconsistent_ids = inconsistent_rows[inconsistent_rows].index

for id in inconsistent_ids:
    flag_2022 = df[(df['ID'] == id) & (df['year'] == 2022)]['Flag'].values

    df.loc[(df['ID'] == id) & (df['year'] == 2021), 'Flag'] = flag_2022[0]

#Fix club logo link consistency
inconsistent_rows = df.groupby('ID')['Club Logo'].nunique() > 1

inconsistent_ids = inconsistent_rows[inconsistent_rows].index

for id in inconsistent_ids:
    club2022 = df[(df['ID'] == id) & (df['year'] == 2022)]['Club'].values
    club2021 = df[(df['ID'] == id) & (df['year'] == 2021)]['Club'].values
    if club2022 == club2021:

        clublogo_2022 = df[(df['ID'] == id) & (df['year'] == 2022)]['Club Logo'].values

        df.loc[(df['ID'] == id) & (df['year'] == 2021), 'Club Logo'] = clublogo_2022[0]

#Remove ClubLogo if player isn't in a club

#locate all rows where Club is empty and set Club logo to None
df.loc[df['Club'] == '', 'Club Logo'] = None

# Format Club Logo links using regex
df['Club Logo'] = df['Club Logo'].str.replace(r'https://cdn.sofifa.com/teams/(\d+)/\D+(\d+).png', r'https://cdn.sofifa.com/teams/\1/\2.png', regex=True)

#Reformat wage
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

#Reformat Value
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

#Release clause
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


#Split work rate to attack and defense
df[['Attack Work Rate', 'Defense Work Rate']] = df['Work Rate'].str.split('/ ', expand=True)


#Split body type and height range into seperate columns
df[['Body Type Only', 'Height Range']] = df['Body Type'].str.split('(', expand=True)
df['Height Range'] = df['Height Range'].str.rstrip(')')


#Remove non standard body types
values = df['Body Type Only'].value_counts()
df = df[df['Body Type Only'].isin(values[values > 1].index)]
df['Body Type Only'].value_counts()
df.head()

#Split Height range into lower and upper bound for detailed analysis
df[['Height Range Lower Bound', 'Height Range Upper Bound']] = (
    df['Height Range'].str.split(r'[+-]', expand=True)
)
mask = df['Height Range'].notna() & df['Height Range'].str.endswith('-')
df.loc[mask, 'Height Range Upper Bound'] = df.loc[mask, 'Height Range Lower Bound']
df.loc[mask, 'Height Range Lower Bound'] = None
df.head()

#Extract player position
df['Position Clean'] = df['Position'].str.extract(r'<.*>(\w*)')
df['Position Clean'].value_counts()

#Transform Joined to date format
df['Joined'] = pd.to_datetime(df['Joined'])

#Extract club from Loaned From
df['Loaned From Club'] = df['Loaned From'].str.extract(r'<[^\<]*>([^\<]*)<[^\<]*>')
df['Loaned From Club'].unique()

#Extract only year from Contract Valid Until
df['Contract Valid Until Year'] = df['Contract Valid Until'].str.extract(r'(\d{4})')
df['Contract Valid Until Year'].value_counts()


#Rename Height and Weight, extract numbers, change to metric
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

#Fix height inconsistency (assume players aren't growing)
inconsistent_rows = df.groupby('ID')['Height_cm'].nunique() > 1

inconsistent_ids = inconsistent_rows[inconsistent_rows].index

for id in inconsistent_ids:
    height_2022 = df[(df['ID'] == id) & (df['year'] == 2022)]['Height_cm'].values

    df.loc[(df['ID'] == id) & (df['year'] == 2021), 'Height_cm'] = height_2022[0]
    

#Fix PreferredFoot - static attribute, use data from 2022 dataset
inconsistent_rows = df.groupby('ID')['Preferred Foot'].nunique() > 1

inconsistent_ids = inconsistent_rows[inconsistent_rows].index

for id in inconsistent_ids:
    foot_2022 = df[(df['ID'] == id) & (df['year'] == 2022)]['Preferred Foot'].values

    df.loc[(df['ID'] == id) & (df['year'] == 2021), 'Preferred Foot'] = foot_2022[0]

#standardise body type - use 2022 data 
inconsistent_rows = df.groupby('ID')['Body Type Only'].nunique() > 1

inconsistent_ids = inconsistent_rows[inconsistent_rows].index

for id in inconsistent_ids:
    body_2022 = df[(df['ID'] == id) & (df['year'] == 2022)]['Body Type Only'].values

    df.loc[(df['ID'] == id) & (df['year'] == 2021), 'Body Type Only'] = body_2022[0]
    
#Change Real Face to boolean values
df.loc[:,'Real Face'] = df['Real Face'].replace({'Yes': True, 'No': False}).astype(bool)
df[['Real Face', 'ID']].head()

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


df_clean = df_clean.copy()
df_clean.rename(columns={"ID": "PlayerID"}, inplace=True)
df_clean.rename(columns={"Club": "ClubName"}, inplace=True)

df_clean.columns = df_clean.columns.str.replace(' ', '')
df_clean.columns = df_clean.columns.str.lower()
df_clean['jerseynumber'] = pd.to_numeric(df_clean['jerseynumber'], errors='coerce').astype('Int64')
df_clean.info()

df_clean.to_csv('data/clean_data.csv', index=False)