--Kojem igraču je vrijednost (value) najviše porasla između dvije godine?

SELECT 
    p1.playerid,
    dp.name,
    (p2.value_euro - p1.value_euro) AS valueincrease
FROM 
    factplayerstats p1
JOIN factplayerstats p2 
    ON p1.playerid = p2.playerid 
    AND p2.yearid = p1.yearid + 1
JOIN dimplayer dp 
    ON p1.playerid = dp.playerid
JOIN dimyear y1 
    ON p1.yearid = y1.yearid
JOIN dimyear y2 
    ON p2.yearid = y2.yearid
ORDER BY 
    valueincrease DESC
LIMIT 1;


--Tko je zaradio najviše novca (wage) kroz dvije godine i koliko?

SELECT 
    f.playerid,
    dp.name,
    SUM(f.wage_euro) AS totalwage
FROM 
    factplayerstats f
JOIN dimplayer dp 
    ON f.playerid = dp.playerid
GROUP BY 
    f.playerid, dp.name
ORDER BY 
    totalwage DESC
LIMIT 1;


--Koji igrač je najdulje u istom klubu?

SELECT 
    dp.name AS player_name,
    dc.clubname,
    MIN(f.joined) AS join_date,
    MAX(f.contractvaliduntil) - EXTRACT (YEAR FROM(MIN(f.joined))) AS duration_years
FROM 
    factplayerstats f
JOIN 
    dimplayer dp 
    ON f.playerid = dp.playerid
JOIN 
    dimclub dc 
    ON f.clubid = dc.clubid
WHERE 
    f.joined IS NOT NULL AND f.contractvaliduntil IS NOT NULL
GROUP BY 
    f.playerid, dp.name, f.clubid, dc.clubname
ORDER BY 
    duration_years DESC
LIMIT 1;

--Koja nacija ima najveću prosječnu kilažu u 2022.?

SELECT 
    dp.nationality,
    AVG(f.weight_kg) AS average_weight_kg
FROM 
    factplayerstats f
JOIN 
    dimplayer dp 
    ON f.playerid = dp.playerid
JOIN 
    dimyear dy 
    ON f.yearid = dy.yearid
WHERE 
    dy.year = 2022
GROUP BY 
    dp.nationality
ORDER BY 
    average_weight_kg DESC
LIMIT 1;

-- Koji klub ima najbolju prosječnu ocjenu po igraču za 2021. i 2022. uz uvjet da klub mora imati barem 11 igrača.

SELECT 
    dc.clubname,
    AVG(f.overall) AS average_overall
FROM 
    factplayerstats f
JOIN 
    dimclub dc 
    ON f.clubid = dc.clubid
GROUP BY 
    dc.clubname
HAVING 
    COUNT(f.playerid) >= 11
ORDER BY 
    average_overall DESC
LIMIT 1;



