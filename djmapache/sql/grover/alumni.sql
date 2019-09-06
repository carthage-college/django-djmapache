SELECT DISTINCT
    ids.id AS cid,
    TRIM(ids.firstname) AS firstname,
    TRIM(NVL(aname_rec.line1,"")) AS alt_name,
    TRIM(ids.lastname) AS lastname,
    TRIM(ids.suffix) AS suffix,
    TRIM(INITCAP(ids.title)) AS prefix,
    TRIM(NVL(email.line1,"")) AS email,
    TRIM(NVL(maiden.lastname,"")) AS birth_last_name,
    CASE
        WHEN TRIM(progs.deg) IN ("BA","BS")
        THEN alum.cl_yr
    END AS grad_yr,
    CASE
        WHEN TRIM(progs.deg) IN ("BA","BS")
        THEN alum.soc_clyr
    END AS soc_yr
FROM
    alum_rec alum
    INNER JOIN
        id_rec ids          ON  alum.id = ids.id
    LEFT JOIN (
        SELECT   prim_id, MAX(active_date) active_date
        FROM     addree_rec
        WHERE    style = "M"
        GROUP BY prim_id
    )
        prevmap             ON  ids.id              = prevmap.prim_id
    LEFT JOIN
        aa_rec as aname_rec
    ON
        (
            ids.id = aname_rec.id AND aname_rec.aa = "ANDR"
        )
    LEFT JOIN
        addree_rec maiden   ON  maiden.prim_id      = prevmap.prim_id
                            AND maiden.active_date  = prevmap.active_date
                            AND maiden.style        = "M"
    LEFT JOIN
        aa_rec email        ON  ids.id              = email.id
                            AND email.aa            = "EML2"
                            AND TODAY
                                BETWEEN
                                    email.beg_date
                                AND
                                    NVL(
                                        email.end_date,
                                        TODAY
                                    )
    LEFT JOIN
        prog_enr_rec progs  ON  ids.id          = progs.id
                            AND progs.acst      = "GRAD"
    LEFT JOIN
        conc_table conc1    ON  progs.conc1     = conc1.conc
    LEFT JOIN
        conc_table conc2    ON  progs.conc2     = conc2.conc
WHERE
    NVL(ids.decsd, "N") = "N"
AND
    email.line1 <> ""
