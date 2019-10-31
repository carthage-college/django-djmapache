SELECT
    provisioning_vw.username, provisioning_vw.id AS cid,
    provisioning_vw.lastname, provisioning_vw.firstname,
    TRIM(NVL(aname_rec.line1,"")) as alt_name,
    TRIM(NVL(maiden.lastname,"")) AS birth_last_name
FROM
    provisioning_vw
LEFT JOIN
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
WHERE
    provisioning_vw.faculty IS NOT NULL
OR
    provisioning_vw.staff IS NOT NULL
ORDER BY
    provisioning_vw.lastname, provisioning_vw.firstname
