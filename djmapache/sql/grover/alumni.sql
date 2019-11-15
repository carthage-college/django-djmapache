SELECT
    'alumni' AS user_type, progs.id AS cid,
    TRIM(progs.lastname || '+' || progs.firstname || '+' || progs.id || '@carthage.college') AS email,
    progs.lastname AS lastname, progs.firstname AS firstname,
    TRIM(NVL(aname_rec.line1,"")) AS alt_name, TRIM(NVL(maiden.lastname,"")) AS birth_last_name,
    TRIM(diplo.firstname) as diploma_firstname, TRIM(diplo.lastname) as diploma_lastname,
    TRIM(
        TRIM(NVL(conc1.txt,"")) || ' ' || TRIM(NVL(conc2.txt,"")) || ' ' || TRIM(NVL(conc3.txt,""))
    ) AS concentration,
    TRIM(NVL(
        CASE WHEN TRIM(progs.deg) IN ("BA","BS") THEN major1.txt ELSE conc1.txt END
    ,'')) || ' ' ||
    TRIM(NVL(
        CASE WHEN TRIM(progs.deg) IN ("BA","BS") THEN major2.txt ELSE conc2.txt END
    ,'')) || ' ' ||
    TRIM(NVL(
        CASE WHEN TRIM(progs.deg) IN ("BA","BS") THEN major3.txt ELSE conc3.txt END
    ,'')) AS majors,
    TRIM(NVL(
        CASE WHEN TRIM(progs.deg) IN ("BA","BS") THEN minor1.txt ELSE conc1.txt END
    ,'')) || ' ' ||
    TRIM(NVL(
        CASE WHEN TRIM(progs.deg) IN ("BA","BS") THEN minor2.txt ELSE conc2.txt END
    ,'')) || ' ' ||
    TRIM(NVL(
        CASE WHEN TRIM(progs.deg) IN ("BA","BS") THEN minor3.txt ELSE conc3.txt END
    ,'')) AS minors,
    CASE WHEN TRIM(progs.deg) IN ("BA","BS") THEN alum.soc_clyr END AS soc_yr,
    progs.grad_yr
FROM
    (
        SELECT
            ALL_GRADS.id, TRIM(IR.lastname) AS lastname, TRIM(IR.firstname) AS firstname,
            CASE WHEN UNDG.id IS NOT NULL THEN UNDG.deg_grant_yr ELSE GRAD.deg_grant_yr END AS grad_yr,
            CASE WHEN UNDG.id IS NOT NULL THEN UNDG.deg ELSE GRAD.deg END AS deg,
            CASE WHEN UNDG.id IS NOT NULL THEN UNDG.major1 ELSE GRAD.major1 END AS major1,
            CASE WHEN UNDG.id IS NOT NULL THEN UNDG.major2 ELSE GRAD.major2 END AS major2,
            CASE WHEN UNDG.id IS NOT NULL THEN UNDG.major3 ELSE GRAD.major3 END AS major3,
            CASE WHEN UNDG.id IS NOT NULL THEN UNDG.minor1 ELSE GRAD.minor1 END AS minor1,
            CASE WHEN UNDG.id IS NOT NULL THEN UNDG.minor2 ELSE GRAD.minor2 END AS minor2,
            CASE WHEN UNDG.id IS NOT NULL THEN UNDG.minor3 ELSE GRAD.minor3 END AS minor3,
            CASE WHEN UNDG.id IS NOT NULL THEN UNDG.conc1 ELSE GRAD.conc1 END AS conc1,
            CASE WHEN UNDG.id IS NOT NULL THEN UNDG.conc2 ELSE GRAD.conc2 END AS conc2,
            CASE WHEN UNDG.id IS NOT NULL THEN UNDG.conc3 ELSE GRAD.conc3 END AS conc3
        FROM
            (
                SELECT
                    id
                FROM
                    prog_enr_rec
                WHERE
                    acst  in ('GRAD','GOOD')
                GROUP BY
                    id
            ) ALL_GRADS
            INNER JOIN
                id_rec IR
            ON
                ALL_GRADS.id = IR.id
            AND
                NVL(IR.decsd, 'N')    =    'N'
            INNER
            JOIN (
                SELECT
                    id
                FROM
                    stu_acad_rec
                WHERE
                    cum_earn_hrs > 65
                GROUP BY id
            ) STU
            ON
                ALL_GRADS.id = STU.id
            LEFT JOIN    prog_enr_rec    UNDG    ON    ALL_GRADS.id     =    UNDG.id
                                                AND    UNDG.prog        =    'UNDG'
                                                AND    UNDG.acst        =    'GRAD'
            LEFT JOIN    prog_enr_rec    GRAD    ON    ALL_GRADS.id     =    GRAD.id
                                                AND    GRAD.prog        =    'GRAD'
                                                AND    GRAD.acst        =    'GRAD'
    )    progs  LEFT JOIN major_table major1     ON    progs.major1     =    major1.major
                LEFT JOIN major_table major2     ON    progs.major2     =    major2.major
                LEFT JOIN major_table major3     ON    progs.major3     =    major3.major
                LEFT JOIN minor_table minor1     ON    progs.minor1     =    minor1.minor
                LEFT JOIN minor_table minor2     ON    progs.minor2     =    minor2.minor
                LEFT JOIN minor_table minor3     ON    progs.minor3     =    minor3.minor
                LEFT JOIN conc_table  conc1      ON    progs.conc1      =    conc1.conc
                LEFT JOIN conc_table  conc2      ON    progs.conc2      =    conc2.conc
                LEFT JOIN conc_table  conc3      ON    progs.conc3      =    conc3.conc
                LEFT JOIN alum_rec    alum       ON    progs.id         =    alum.id
                LEFT JOIN addree_rec  diplo      ON    progs.id         =    diplo.prim_id
                                                AND    diplo.style      =    "D"
                                                AND    NVL(diplo.inactive_date, TODAY) >= TODAY
                LEFT JOIN aa_rec    aname_rec    ON    progs.id         =    aname_rec.id
                                                AND    aname_rec.aa     =    "ANDR"
                LEFT JOIN (
                    SELECT
                        prim_id, MAX(active_date) AS active_date
                    FROM
                        addree_rec
                    WHERE
                        style = "M"
                    GROUP BY prim_id
                ) prevmap
                ON
                    progs.id = prevmap.prim_id
                LEFT JOIN addree_rec    maiden   ON    prevmap.prim_id  =    maiden.prim_id
                                                AND    prevmap.active_date    =    maiden.active_date
                                                AND    maiden.style     =    "M"
ORDER BY
    lastname, firstname
