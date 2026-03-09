--check how many rows there are 
SELECT COUNT(*) FROM public.unemployment;

--count unemployment by area type
SELECT 
        area_type,
        COUNT(DISTINCT area_name)
FROM 
        public.unemployment 
GROUP BY area_type;

--shows the mismatched calculations between labor_force and employment+unemployment
WITH calculated AS (
    SELECT 
        labor_force,
        employment + unemployment AS total_labor,
        labor_force - (employment + unemployment) AS raw_diff
    FROM 
        public.unemployment 
    WHERE 
        area_type = 'State'
)
SELECT 
    labor_force,
    total_labor,
    raw_diff,
    CASE 
        WHEN labor_force = total_labor THEN 'Exact match'
        WHEN ABS(raw_diff) <= 100 THEN 'Small mismatch'
        WHEN ABS(raw_diff) <= 1000 THEN 'Medium mismatch'
        ELSE 'Large mismatch'
    END AS mismatch_flag,
    ROUND(ABS(raw_diff) / NULLIF(total_labor, 0) * 100, 6) AS pct_difference
FROM calculated
ORDER BY ABS(raw_diff) DESC;

--find the highest unemployment by Metropolitan Area
SELECT DISTINCT ON (year)
    year,
    area_name,
    ROUND(unemployment_rate::NUMERIC, 2) AS highest_rate
FROM public.unemployment 
WHERE area_type = 'Metropolitan Area'
ORDER BY year, unemployment_rate DESC;

--find the highest employment by Metropolitan Area
SELECT DISTINCT ON (year)
    year,
    area_name,
    ROUND(employment::NUMERIC, 2) AS highest_rate
FROM public.unemployment 
WHERE area_type = 'Metropolitan Area'
ORDER BY year, employment DESC;

--Find the average unemployment by area_type for each year to determine which year has the highest unemploy
SELECT 
        area_type, 
        year, 
        AVG(unemployment_rate) as avg_unemploy
FROM 
        public.unemployment 
WHERE area_type = 'Metropolitan Area'
GROUP BY 2, 1
ORDER BY 3 DESC;

--highest unemployment for each area_type 
WITH ranked_years AS (
    SELECT 
        area_type, 
        year, 
        ROUND(AVG(unemployment_rate)::NUMERIC, 2) AS avg_unemploy,
        ROW_NUMBER() OVER (PARTITION BY area_type ORDER BY AVG(unemployment_rate) DESC) AS rank
    FROM public.unemployment 
    GROUP BY area_type, year
)
SELECT 
    area_type, 
    year, 
    avg_unemploy
FROM ranked_years
WHERE rank = 1
ORDER BY avg_unemploy DESC;

--highest employment for each area_type 
WITH highest_employ AS (
    SELECT 
        area_type, 
        year, 
        employment,
        ROW_NUMBER() OVER (PARTITION BY area_type ORDER BY AVG(employment) DESC) AS rank
    FROM public.unemployment 
    GROUP BY area_type, year, employment
)
SELECT 
    area_type, 
    year, 
    employment
FROM highest_employ
WHERE rank = 1
ORDER BY employment DESC;

--avg employment by year
WITH ranked_years AS (
    SELECT 
        year, 
        AVG(employment) as avg_employ,
        AVG(unemployment) as avg_unemploy,
        ROW_NUMBER() OVER (PARTITION BY year ORDER BY AVG(employment) DESC) AS employ_rank,
        ROW_NUMBER() OVER (PARTITION BY year ORDER BY AVG(employment) DESC) AS unemploy_rank
    FROM public.unemployment 
    WHERE area_type = 'State'
    GROUP BY  year
)
SELECT 
    year, 
    avg_employ, 
    avg_unemploy
FROM ranked_years
--WHERE employ_rank = 1
ORDER BY year, avg_employ DESC;
