SELECT
    "001" AS bnUnitNo, bnTerm, SUBSTR(tfc.yr,3,2) AS bnYear,
    TRIM(LEFT(sr.crs_no,4)) AS bnDept, TRIM(SUBSTR(sr.crs_no,5,8)) AS bnCourseNo,
    TRIM(sr.sec_no) AS bnSectionNo, TRIM(LEFT(ir.fullname,20)) AS bnProfName,
    MAX(sr.max_reg) AS bnMaxCapcty, MAX(sr.reg_num) AS bnEstEnrlmnt,
    MAX(sr.reg_num) AS bnActEnrlmnt, "" AS bnContClss, "" AS bnEvngClss,
    "" AS bnExtnsnClss, "" AS bnTxtnetClss, "" AS bnLoctn,
    TRIM(LEFT(cr.title1,25)) AS bntCourseTitl,
    TRIM(sr.crs_no || " " || sr.sec_no) AS bnCourseID
FROM
    sec_rec sr
        INNER JOIN
        (SELECT acr.acyr AS calyr, TRIM(acr.sess) AS sess, YEAR(acr.end_date) AS yr,
            CASE
                WHEN sess = 'AA' THEN 45
                WHEN sess = 'AB' THEN 60
                WHEN sess = 'AG' THEN 45
                WHEN sess = 'AK' THEN 75
                WHEN sess = 'AM' THEN 45
                WHEN sess = 'AS' THEN 25
                WHEN sess = 'AT' THEN 45
                WHEN sess = 'GA' THEN 45
                WHEN sess = 'GB' THEN 45
                WHEN sess = 'GC' THEN 45
                WHEN sess = 'GE' THEN 25
                WHEN sess = 'RA' THEN 21
                WHEN sess = 'RB' THEN 30
                WHEN sess = 'RC' THEN 21
                WHEN sess = 'RE' THEN 25
                ELSE 99
            END AS pre_grace,
            CASE
                WHEN sess = "AA" THEN 45
                WHEN sess = "AB" THEN 20
                WHEN sess = "AG" THEN 35
                WHEN sess = "AK" THEN 52
                WHEN sess = "AM" THEN 36
                WHEN sess = "AS" THEN 45
                WHEN sess = "AT" THEN 10
                WHEN sess = "GA" THEN 30
                WHEN sess = "GB" THEN 4
                WHEN sess = "GC" THEN 19
                WHEN sess = 'GE' THEN 45
                WHEN sess = "RA" THEN 42
                WHEN sess = "RB" THEN 2
                WHEN sess = "RC" THEN 15
                WHEN sess = 'RE' THEN 45
                ELSE 99
            END AS post_grace,
            CASE
                WHEN sess = "AA" THEN "G"
                WHEN sess = "AB" THEN "G"
                WHEN sess = "AG" THEN "J"
                WHEN sess = "AK" THEN "S"
                WHEN sess = "AM" THEN "S"
                WHEN sess = "AS" THEN "B"
                WHEN sess = "AT" THEN "B"
                WHEN sess = "GA" THEN "F"
                WHEN sess = "GB" THEN "I"
                WHEN sess = "GC" THEN "W"
                WHEN sess = 'GE' THEN "A"
                WHEN sess = "RA" THEN "F"
                WHEN sess = "RB" THEN "I"
                WHEN sess = "RC" THEN "W"
                WHEN sess = 'RE' THEN "A"
                ELSE "z"
            END AS bnTerm
        FROM acad_cal_rec acr
        WHERE end_date-0 >= TODAY
        AND subsess= ""
        AND sess IN ("AA","AB","AG","AK","AM","AS","AT","GA","GB","GC", "GE", "RA",
                    "RB","RC","RE")) tfc ON tfc.sess = sr.sess
            INNER JOIN id_rec ir ON sr.fac_id = ir.id
            INNER JOIN crs_rec cr ON sr.crs_no = cr.crs_no
WHERE
    tfc.yr = sr.yr
AND
    sr.cat = cr.cat
AND
    sr.stat IN ("R","O","C")
GROUP BY
    bnUnitNo, bnTerm, bnYear, bnDept, bnCourseNo, bnSectionNo, bnProfName,
    bntCourseTitl, bnCourseID
ORDER BY
    bnDept, bnCourseNo, bnYear, bnSectionNo;
