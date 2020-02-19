-- builds academic calendar for active terms with pre & post grace periods
-- per term.
-- modified query from Ron L. 1-17-2018 (changed RB from 10 to 30)
-- the date logic for ePullGrp was changed to use they dayofyear calculations
-- in the following three queries.
-- dates provided by Pam Robers: Apr 25, Aug 5 and Dec 3.

SELECT
    acyr, sess, yr, eTermGrp, ePullGrp, eBegDate,
    TO_CHAR(beg_date, '%m/%d/%Y') AS beg_date,
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
                WHEN sess IN ("AA","AB","RA","GA") THEN TRIM('09/01/'|| TO_CHAR(acad_cal_rec.yr))
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
        WHERE acad_cal_rec.acyr = CASE WHEN MONTH(TODAY + 21) >= 9 THEN MOD(YEAR(TODAY), 100) || MOD(YEAR(TODAY) + 1, 100)
                                                              ELSE MOD(YEAR(TODAY) - 1, 100) || MOD(YEAR(TODAY), 100) END
        AND
            acad_cal_rec.subsess = ""
        AND
            acad_cal_rec.prog IN ('UNDG','GRAD')
    )   grouped
WHERE
    grouped.eTermGrp    =   grouped.ePullGrp
ORDER BY
    grouped.yr, grouped.beg_date
