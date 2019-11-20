SELECT DISTINCT
    'alumni' as user_type,
    TRIM(
        ids.lastname || '+' ||
        ids.firstname || '+' ||
         ids.id || '@carthage.college'
    ) as email,
    ids.id AS cid, TRIM(ids.lastname) AS lastname, TRIM(ids.firstname) AS firstname,
    TRIM(NVL(aname_rec.line1,"")) AS alt_name, TRIM(NVL(maiden.lastname,"")) AS birth_last_name,
    TRIM(diplo.firstname) as diploma_firstname,
    TRIM(diplo.lastname) as diploma_lastname,
    TRIM(
        TRIM(NVL(conc1.txt,"")) || ' ' ||
        TRIM(NVL(conc2.txt,"")) || ' ' ||
        TRIM(NVL(conc3.txt,""))
    ) as concentration,
    TRIM(NVL(
        CASE
            WHEN TRIM(progs.deg) IN ("BA","BS")
            THEN major1.txt
            ELSE conc1.txt
        END
    ,'')) || ' ' ||
    TRIM(NVL(
        CASE
            WHEN TRIM(progs.deg) IN ("BA","BS")
            THEN major2.txt
            ELSE conc2.txt
        END
    ,'')) || ' ' ||
    TRIM(NVL(
        CASE
            WHEN TRIM(progs.deg) IN ("BA","BS")
            THEN major3.txt
            ELSE conc3.txt
        END
    ,'')) AS majors,
    TRIM(NVL(
        CASE
            WHEN TRIM(progs.deg) IN ("BA","BS")
            THEN minor1.txt
            ELSE conc1.txt
        END
    ,'')) || ' ' ||
    TRIM(NVL(
        CASE
            WHEN TRIM(progs.deg) IN ("BA","BS")
            THEN minor2.txt
            ELSE conc2.txt
        END
    ,'')) || ' ' ||
    TRIM(NVL(
        CASE
            WHEN TRIM(progs.deg) IN ("BA","BS")
            THEN minor3.txt
            ELSE conc3.txt
        END
    ,'')) AS minors,
    CASE
        WHEN TRIM(progs.deg) IN ("BA","BS")
        THEN alum.soc_clyr
    END AS soc_yr,
    CASE
        WHEN TRIM(progs.deg) IN ("BA","BS")
        THEN alum.cl_yr
    END AS grad_yr
FROM
    alum_rec alum
INNER JOIN
    id_rec ids
ON
    alum.id = ids.id
LEFT JOIN
    addree_rec diplo
ON
    ids.id = diplo.prim_id
AND
    diplo.style= "D"
AND
    NVL(diplo.inactive_date, TODAY) >= TODAY
LEFT JOIN (
    SELECT
        prim_id, MAX(active_date) active_date
    FROM
        addree_rec
    WHERE
        style = "M"
    GROUP BY prim_id
    )
    prevmap
ON
    ids.id = prevmap.prim_id
LEFT JOIN
    aa_rec as aname_rec
ON
    (
        ids.id = aname_rec.id AND aname_rec.aa = "ANDR"
    )
LEFT JOIN
    addree_rec maiden
ON
    prevmap.prim_id = maiden.prim_id
AND
    prevmap.active_date = maiden.active_date
AND
    maiden.style = "M"
LEFT JOIN
    prog_enr_rec progs
ON
    ids.id = progs.id
AND
    progs.acst = "GRAD"
AND (
    alum.cl_yr = progs.deg_grant_yr
OR
    alum.soc_clyr = progs.deg_grant_yr
)
LEFT JOIN
    major_table major1  ON  progs.major1 = major1.major
LEFT JOIN
    major_table major2  ON  progs.major2 = major2.major
LEFT JOIN
    major_table major3  ON  progs.major3 = major3.major
LEFT JOIN
    minor_table minor1  ON  progs.minor1 = minor1.minor
LEFT JOIN
    minor_table minor2  ON  progs.minor2 = minor2.minor
LEFT JOIN
    minor_table minor3  ON  progs.minor3 = minor3.minor
LEFT JOIN
    conc_table conc1    ON  progs.conc1  = conc1.conc
LEFT JOIN
    conc_table conc2    ON  progs.conc2  = conc2.conc
LEFT JOIN
    conc_table conc3    ON  progs.conc3  = conc3.conc
WHERE
    NVL(ids.decsd, "N") = "N"
ORDER BY
    lastname, firstname
