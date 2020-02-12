SELECT
    lastname, firstname, middlename, id, addr_line1, addr_line2,
    city, st,
    TRIM(NVL(INITCAP(ctry_table.txt), directory_vw.ctry)) AS ctry,
    zip, phone, email,
        MAX(
            CASE grouping
                WHEN    'Faculty'   THEN    3
                WHEN    'Staff'     THEN    2
                WHEN    'Student'   THEN    1
                                    ELSE    0
            END
            )
    AS groupIndex, grouping,
    TO_CHAR(TODAY + 1 UNITS YEAR, '%Y-%m-%d') || 'T12:00:00' AS expirationDate
FROM
    directory_vw
LEFT JOIN
    ctry_table
ON
    directory_vw.ctry = ctry_table.ctry
GROUP BY
    lastname, firstname, middlename, id, addr_line1, addr_line2,
    city, st, ctry, zip, phone, email, grouping
ORDER BY
    lastname, firstname, email
