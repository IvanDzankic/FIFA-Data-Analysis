# FIFA-Data-Analysis

Zadatak u sklopu CROZ Ljetnog akceleratora koji uključuje modeliranje podataka, pisanje SQL upita te kreaciju vizualnog prikaza podataka.


## Korištena tehnologija

- **PostgreSQL** - Relacijska baza podataka za pohranu obrađenog dataseta
- **pgAdmin4** - Grafičko sučelje za upravljanje PostgreSQL bazom podataka
- **PowerBI** - Alat za vizualizaciju podataka
- **Docker i Docker Compose** - Alati za postavljanje razvojnog okruženja (Docker projekt dijeli u kontejnere, a Docker Compose povezuje i pokreće servise)
- **Python** - Programski jezik za rad s podacima

### Korištene Python biblioteke

- **pandas** - Glavna biblioteka za rad s tabličnim podacima i pripremu podataka za pohranu u bazu podataka
- **sqlalchemy** - Korištena za povezivanje s bazom podataka te unos podataka
- **psycopg2** - PostgreSQL adapter za Python, također korišten u svrhu povezivanja s bazom podataka te direktnim izvršavanjem skripte za kreaciju baze podataka `db_creation.sql`

## Pokretanje

### Preduvjeti

Za pokretanje projekta potrebno je imati instalirano:
- Docker
- Docker Compose

### Struktura projekta

- `data/`: Sadrži ulazni dataset
- `scripts/`: Sadrži Python i SQL skripte korištene za kreaciju baze podataka, transformaciju i učitavanje podataka u bazu
- `Dockerfile`: Kreira Docker image za projekt
- `docker-compose.yml`: Definira servise koje Docker kreira
- `requirements.txt`: Sadrži potrebne biblioteke za pokretanje skripti
- `run.sh`: Skripta za pokretanje projekta

### Kloniranje i pokretanje

```bash
git clone https://github.com/IvanDzankic/FIFA-Data-Analysis.git
cd FIFA-Data-Analysis
```
Nakon pozicioniranja u direktorij potrebno je buildati projekt:
```
docker-compose up --build
```

### Pregled podataka

Za pregled podataka moguće je koristiti alat pgAdmin4.
Nakon pokretanja, potrebno je:
- Dodati novi server: Desni klik na "Servers" > "Register" > "Server"
- U "Connection" unijeti podatke:
    - Host name/address: localhost
    - Port: 5432
    - Maintenance database: fifa_db
    - Username: fifa_user
    - Password: fifa_password
- Save
- Tablice je sada moguće pregledati u "Schemas > public > tables"
- Pomoću query toola moguće je i pokrenuti upite iz `scripts/sql_upiti.sql` koji odgovaraju na pitanja zadana u zadatku
- Vizualni prikaz podataka nalazi se u PowerBi izvješću `report.pbix`

ERD dijagram nastale baze podataka:

![Untitled](https://github.com/user-attachments/assets/db1f01f1-de73-45dc-8e12-2949de34a64e)
