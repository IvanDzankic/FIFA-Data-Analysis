DROP TABLE IF EXISTS FactPlayerStats;
DROP TABLE IF EXISTS DimWorkRate;
DROP TABLE IF EXISTS DimPosition;
DROP TABLE IF EXISTS DimYear;
DROP TABLE IF EXISTS DimClub;
DROP TABLE IF EXISTS DimPlayer;

CREATE TABLE DimPlayer (
    PlayerID INT PRIMARY KEY,
    Name VARCHAR(255),
    Photo VARCHAR(255),
    Nationality VARCHAR(255),
    Flag VARCHAR(255),
    PreferredFoot VARCHAR(50),
    BodyType VARCHAR(50),
    HeightRange VARCHAR(50),
    HeightRangeLowerBound INT,
    HeightRangeUpperBound INT,
    Height_cm INT,
    RealFace BOOLEAN
);

CREATE TABLE DimClub (
    ClubID SERIAL PRIMARY KEY,
    ClubName VARCHAR(255),
    ClubLogo VARCHAR(255)
);

CREATE TABLE DimYear (
    YearID SERIAL PRIMARY KEY,
    Year INT
);

CREATE TABLE DimPosition (
    PositionID SERIAL PRIMARY KEY,
    Position VARCHAR(50)
);

CREATE TABLE DimWorkRate (
    WorkRateID SERIAL PRIMARY KEY,
    WorkRateValue VARCHAR(50)
);

CREATE TABLE FactPlayerStats (
    YearID INT,
    PlayerID INT,
    ClubID INT,
    PositionID INT,
    BestPositionID INT,
    AttackWorkRateID INT,
    DefenseWorkRateID INT,
	LoanedFromID INT,
    Age INT,
    JerseyNumber INT,
    Overall INT,
    Potential INT,
    Value_Euro FLOAT,
    Wage_Euro FLOAT,
    Special INT,
    InternationalReputation FLOAT,
    WeakFoot FLOAT,
    SkillMoves FLOAT,
    Joined DATE,
    ContractValidUntil INT,
    Weight_kg INT,
    Crossing FLOAT,
    Finishing FLOAT,
    HeadingAccuracy FLOAT,
    ShortPassing FLOAT,
    Volleys FLOAT,
    Dribbling FLOAT,
    Curve FLOAT,
    FKAccuracy FLOAT,
    LongPassing FLOAT,
    BallControl FLOAT,
    Acceleration FLOAT,
    SprintSpeed FLOAT,
    Agility FLOAT,
    Reactions FLOAT,
    Balance FLOAT,
    ShotPower FLOAT,
    Jumping FLOAT,
    Stamina FLOAT,
    Strength FLOAT,
    LongShots FLOAT,
    Aggression FLOAT,
    Interceptions FLOAT,
    Positioning FLOAT,
    Vision FLOAT,
    Penalties FLOAT,
    Composure FLOAT,
    Marking FLOAT,
    StandingTackle FLOAT,
    SlidingTackle FLOAT,
    GKDiving FLOAT,
    GKHandling FLOAT,
    GKKicking FLOAT,
    GKPositioning FLOAT,
    GKReflexes FLOAT,
    BestOverallRating FLOAT,
    ReleaseClause_Euro FLOAT,
    DefensiveAwareness FLOAT,
    FOREIGN KEY (YearID) REFERENCES DimYear(YearID),
    FOREIGN KEY (PlayerID) REFERENCES DimPlayer(PlayerID),
    FOREIGN KEY (ClubID) REFERENCES DimClub(ClubID),
    FOREIGN KEY (PositionID) REFERENCES DimPosition(PositionID),
    FOREIGN KEY (AttackWorkRateID) REFERENCES DimWorkRate(WorkRateID),
    FOREIGN KEY (DefenseWorkRateID) REFERENCES DimWorkRate(WorkRateID),
    FOREIGN KEY (BestPositionID) REFERENCES DimPosition(PositionID),
	FOREIGN KEY (LoanedFromID) REFERENCES DimClub(ClubID)

);
