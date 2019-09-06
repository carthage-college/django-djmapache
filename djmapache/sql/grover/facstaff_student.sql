SELECT
    provisioning_vw.lastname, provisioning_vw.firstname,
    TRIM(aname_rec.line1) as alt_name,
    TRIM(NVL(maiden.lastname,"")) AS birth_last_name,
    provisioning_vw.username, 
    provisioning_vw.id AS cid
FROM
    provisioning_vw
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
    provisioning_vw.students is not null
ORDER BY
    provisioning_vw.lastname, provisioning_vw.firstname
