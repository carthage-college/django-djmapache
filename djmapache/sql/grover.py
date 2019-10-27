"""
    'User Type','Email Address','Database Key','First Name','Last Name',
    'Preferred Name','Previous Last Name',
    'Transcript First Name','Transcript Last Name',
    'Concentration','Majors Admin Only','Minors Admin Only',
    'Social Class Year','Grad Year',
"""
FACSTAFF_STUDENT = '''
SELECT
    '{}' as user_type,
    provisioning_vw.username, provisioning_vw.id AS cid,
    provisioning_vw.lastname, provisioning_vw.firstname,
    TRIM(NVL(aname_rec.line1,"")) as alt_name,
    TRIM(NVL(maiden.lastname,"")) AS birth_last_name,
    {}
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
    ,'')) AS minors,
    "" as tran_first_name,
    "" as tran_last_name
FROM
    provisioning_vw
INNER JOIN
    prog_enr_rec ON  provisioning_vw.id = prog_enr_rec.id
{}
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
{}
ORDER BY
    provisioning_vw.lastname, provisioning_vw.firstname
'''.format

"""
        grad_yr_field = '"" as grad_yr,'
        grad_yr_join = ''
        grad_yr_where = ''
        if who == 'student':
            grad_yr_field = 'prog_enr_rec.plan_grad_yr as grad_yr,'
            grad_yr_join = '''
                LEFT JOIN
                    prog_enr_rec
                ON
                    provisioning_vw.id = prog_enr_rec.id
            '''
            grad_yr_where = '''
                AND prog_enr_rec.lv_date IS NULL
                AND prog_enr_rec.plan_grad_yr != 0
            '''
            where = 'provisioning_vw.student IS NOT NULL'
        sql = FACSTAFF_STUDENT(grad_yr_field, grad_yr_join, where, grad_yr_where)
"""
ALUMNI = '''
SELECT DISTINCT
    ids.id AS cid,
    TRIM(ids.firstname) AS firstname,
    TRIM(NVL(aname_rec.line1,"")) AS alt_name,
    TRIM(ids.lastname) AS lastname,
    TRIM(ids.suffix) AS suffix,
    TRIM(INITCAP(ids.title)) AS prefix,
    TRIM(NVL(email1.line1,"")) AS email1,
    TRIM(NVL(email2.line1,"")) AS email2,
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
        aa_rec email1        ON  ids.id              = email1.id
                            AND email1.aa            = "EML1"
    LEFT JOIN
        aa_rec email2        ON  ids.id              = email2.id
                            AND email2.aa            = "EML2"
                            AND TODAY
                                BETWEEN
                                    email2.beg_date
                                AND
                                    NVL(
                                        email2.end_date,
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
'''
