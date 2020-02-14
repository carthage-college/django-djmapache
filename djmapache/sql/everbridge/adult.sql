SELECT
    TRIM(IDrec.firstname) AS firstname, IDrec.middlename[1,1] AS middleinitial,
    TRIM(IDrec.lastname) AS lastname, TRIM(IDrec.suffixname) AS suffix,
    IDrec.id ExternalID, 'United States' AS Country,
    'Carthage College' AS BusinessName, 'Adult Students' AS RecordType,
    ENSrec.phone AS Phone1, 'United States' AS PhoneCountry1,
    TRIM(EMLrec.line1) AS EmailAddress1,
    TRIM(ENSrec.line1) || TRIM(ENSrec.line2) AS EmailAddress2,
    CASE
        WHEN NVL(ENSrec.opt_out, 1) =    1 THEN ENSrec.phone
                                            ELSE    ''
    END AS SMS1, 'United States' AS SMS1Country, 'Standing' AS CustomField1,
    'Adult Student' AS CustomValue1, 'Dormitory' as CustomField2,
    'Commuter' AS CustomValue2, 'Parking Lot' AS CustomField3,
    'CMTR' AS CustomValue3,'END' AS END
FROM
    id_rec  IDrec   INNER JOIN  stu_acad_rec SArec   ON  IDrec.id   =   SArec.id
                    INNER JOIN  acad_cal_rec    ACrec   ON  SArec.yr    =   ACrec.yr
                                                        AND SArec.sess  =   ACrec.sess
                    LEFT JOIN   aa_rec          ENSrec  ON  IDrec.id    =   ENSrec.id
                                                        AND ENSrec.aa   =   'ENS'
                                                        AND TODAY   BETWEEN ENSrec.beg_date AND NVL(ENSrec.end_date, TODAY)
                    LEFT JOIN   aa_rec          EMLrec  ON  IDrec.id    =   EMLrec.id
                                                        AND EMLrec.aa   =   'EML1'
                                                        AND TODAY   BETWEEN EMLrec.beg_date AND NVL(EMLrec.end_date, TODAY)
WHERE
    ACrec.yr    =   YEAR(TODAY)
AND
    ACrec.sess  IN  (SELECT sess FROM sess_table WHERE prog IN ('GRAD','PARA','PRDV')
    AND TODAY BETWEEN active_date AND NVL(inactive_date, TODAY))
AND
    TODAY   BETWEEN ACrec.beg_date AND ACrec.end_date
GROUP BY
    IDrec.id, IDrec.firstname, IDrec.lastname, IDrec.middlename[1,1],
    IDrec.suffixname, Phone1, EmailAddress1, EmailAddress2, SMS1
ORDER BY
    lastname, firstname
