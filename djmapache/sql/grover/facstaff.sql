SELECT
    provisioning_vw.username, provisioning_vw.id AS cid,
    provisioning_vw.lastname, provisioning_vw.firstname,
    TRIM(NVL(aname_rec.line1,"")) as alt_name,
    TRIM(NVL(maiden.lastname,"")) AS birth_last_name,
    --conc1.txt,conc2.txt,conc3.txt,
    --concat(
    -- TRIM(NVL(conc1.txt,"")), 
    -- concat( TRIM(NVL(conc2.txt,"")), TRIM(NVL(conc3.txt,"")) )
    --) as con,
    --COALESCE(conc1.txt, '') || COALESCE(conc2.txt, '') || COALESCE(conc3.txt, '') as con,
    TRIM(
        NVL(conc1.txt,"")) || TRIM(NVL(conc2.txt,"")) || TRIM(NVL(conc3.txt,"")
    ) as consentration,
    TRIM(NVL(
        CASE
            WHEN TRIM(prog_enr_rec.deg) IN ("BA","BS")
            THEN major1.txt
            ELSE conc1.txt
        END
    ,'')) || ' ' ||
    TRIM(NVL(
        CASE
            WHEN TRIM(prog_enr_rec.deg) IN ("BA","BS")
            THEN major2.txt
            ELSE conc2.txt
        END
    ,'')) || ' ' ||
    TRIM(NVL(
        CASE
            WHEN TRIM(prog_enr_rec.deg) IN ("BA","BS")
            THEN major3.txt
            ELSE conc3.txt
        END
    ,'')) AS majors,
    TRIM(NVL(
        CASE
            WHEN TRIM(prog_enr_rec.deg) IN ("BA","BS")
            THEN minor1.txt
            ELSE conc1.txt
        END
    ,'')) || ' ' ||
    TRIM(NVL(
        CASE
            WHEN TRIM(prog_enr_rec.deg) IN ("BA","BS")
            THEN minor2.txt
            ELSE conc2.txt
        END
    ,'')) || ' ' ||
    TRIM(NVL(
        CASE
            WHEN TRIM(prog_enr_rec.deg) IN ("BA","BS")
            THEN minor3.txt
            ELSE conc3.txt
        END
    ,'')) AS minors
FROM
    provisioning_vw
INNER JOIN
    prog_enr_rec ON  provisioning_vw.id = prog_enr_rec.id
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
    provisioning_vw.id = prevmap.prim_id
LEFT JOIN
    addree_rec maiden
ON
    prevmap.prim_id = maiden.prim_id
AND
    prevmap.active_date = maiden.active_date
AND
    maiden.style = "M"
LEFT JOIN
    aa_rec AS aname_rec
ON
    (provisioning_vw.id = aname_rec.id AND aname_rec.aa = "ANDR")
LEFT JOIN
    major_table major1  ON  prog_enr_rec.major1 = major1.major
LEFT JOIN
    major_table major2  ON  prog_enr_rec.major2 = major2.major
LEFT JOIN
    major_table major3  ON  prog_enr_rec.major3 = major3.major
LEFT JOIN
    minor_table minor1  ON  prog_enr_rec.minor1 = minor1.minor
LEFT JOIN
    minor_table minor2  ON  prog_enr_rec.minor2 = minor2.minor
LEFT JOIN
    minor_table minor3  ON  prog_enr_rec.minor3 = minor3.minor
LEFT JOIN
    conc_table conc1    ON  prog_enr_rec.conc1  = conc1.conc
LEFT JOIN
    conc_table conc2    ON  prog_enr_rec.conc2  = conc2.conc
LEFT JOIN
    conc_table conc3    ON  prog_enr_rec.conc3  = conc3.conc
WHERE
    provisioning_vw.faculty IS NOT NULL
OR
    provisioning_vw.staff IS NOT NULL
ORDER BY
    provisioning_vw.lastname, provisioning_vw.firstname
