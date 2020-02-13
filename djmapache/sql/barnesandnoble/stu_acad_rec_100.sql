-- fetch active students and sets budget limit for export
-- (books = '100' & 3000.00) and active UBAL holds
SELECT
    sar.id AS Userid, TRIM(ir.lastname) AS Elastname, TRIM(ir.firstname) AS Efirstname,
    UPPER(LEFT(ir.middlename,1)) AS Xmiddleinit,
    CASE
        WHEN tmpU.id IS NOT NULL THEN 0
                                 ELSE 300000
    END AS Xcred_limit, 100 AS EProviderCode, MIN(tas.eBegDate) AS Ebegdate,
    MAX(tas.eEndDate) AS Eenddate, "" AS Eidtype, "" AS Erecordtype, "D" AS Eaccttype
FROM
    stu_acad_rec sar
    INNER JOIN id_rec ir ON sar.id = ir.id
    INNER JOIN
        (SELECT
            acyr, sess, yr, eTermGrp, ePullGrp, eBegDate, TO_CHAR(beg_date, '%m/%d/%Y') AS beg_date,
            eEndDate, TO_CHAR(end_date, '%m/%d/%Y') AS end_date, subsess, prog
        FROM
            (
                SELECT
                    acad_cal_rec.acyr, TRIM(acad_cal_rec.sess) AS sess, acad_cal_rec.yr,
                    CASE
                        WHEN sess IN ("AA","AB","RA","GA") THEN 'Fall'
                        WHEN sess IN ("AG","AK","AM","GB","GC","RB","RC") THEN 'Spring'
                        WHEN sess IN ("AS","AT","GE","RE") THEN 'Summer'
                                                           ELSE 'Neutral'
                    END AS eTermGrp,
                    CASE
                        WHEN today - mdy(1,1,year(today))+1 < mdy(4,26,year(today)) - mdy(1,1,year(today))+1 THEN 'Spring'
                        WHEN today - mdy(1,1,year(today))+1 < mdy(8,5,year(today))  - mdy(1,1,year(today))+1 THEN 'Summer'
                        WHEN today - mdy(1,1,year(today))+1 < mdy(12,3,year(today)) - mdy(1,1,year(today))+1 THEN 'Fall'
                        ELSE 'Spring'
                    END AS ePullGrp,
                    CASE
                        WHEN sess IN ("AA","AB","RA","GA") THEN TRIM('8/11/'|| TO_CHAR(acad_cal_rec.yr))
                        WHEN sess IN ("AG","AK","AM","GB","GC","RB","RC") THEN TRIM('01/01/' || TO_CHAR(acad_cal_rec.yr))
                        WHEN sess IN ("AS","AT","GE","RE") THEN TRIM('05/26/' || TO_CHAR(acad_cal_rec.yr))
                                                           ELSE TRIM('08/01/' || TO_CHAR(acad_cal_rec.yr))
                    END AS eBegDate,
                    acad_cal_rec.beg_date,
                    CASE
                        WHEN sess IN ("AA","AB","RA","GA") THEN TRIM('12/24/'|| TO_CHAR(acad_cal_rec.yr))
                        WHEN sess IN ("AG","AK","AM","GB","GC","RB","RC") THEN TRIM('05/25/' || TO_CHAR(acad_cal_rec.yr))
                        WHEN sess IN ("AS","AT","GE","RE") THEN TRIM('07/30/' || TO_CHAR(acad_cal_rec.yr))
                                                           ELSE TRIM('08/1/' || TO_CHAR(acad_cal_rec.yr))
                    END AS eEndDate,
                    acad_cal_rec.end_date, acad_cal_rec.subsess, acad_cal_rec.prog
                FROM acad_cal_rec
                WHERE acad_cal_rec.acyr = CASE WHEN today - mdy(1,1,year(today))+1 < mdy(4,26,year(today)) - mdy(1,1,year(today))+1 THEN MOD(YEAR(TODAY), 100) - 1 || MOD(YEAR(TODAY), 100)
                                           WHEN today - mdy(1,1,year(today))+1 < mdy(8,5,year(today))  - mdy(1,1,year(today))+1 THEN MOD(YEAR(TODAY), 100) - 1 || MOD(YEAR(TODAY), 100)
                                               WHEN today - mdy(1,1,year(today))+1 < mdy(12,3,year(today)) - mdy(1,1,year(today))+1 THEN MOD(YEAR(TODAY), 100) || MOD(YEAR(TODAY) + 1, 100)
                                           ELSE MOD(YEAR(TODAY), 100) || MOD(YEAR(TODAY), 100) + 1
                                          END
                AND
                    acad_cal_rec.subsess = ""
                AND
                    acad_cal_rec.prog IN ('UNDG','GRAD')
            )   grouped
        WHERE
            grouped.eTermGrp    =   grouped.ePullGrp
        ORDER BY
            grouped.yr, grouped.beg_date) as tas ON sar.sess = tas.sess
        LEFT JOIN
            (SELECT
                id
            FROM
                hold_rec
            WHERE
                hld ="UBAL"
            AND (end_date IS NULL or end_date > TODAY)) tmpU ON sar.id = tmpU.id
WHERE
    tas.yr = sar.yr
    AND sar.subprog IN ("TRAD","PTSM","TRAP","YOP","7WK","MED","ACT")
    AND sar.reg_hrs > 0
    AND (sar.reg_stat = "R" OR sar.reg_stat = "C")
GROUP BY
    sar.id, Elastname, Efirstname, Xmiddleinit, Xcred_limit,
    EProviderCode, Eidtype, Erecordtype, Eaccttype
ORDER BY Elastname, Efirstname
