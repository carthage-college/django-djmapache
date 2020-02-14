SELECT UNIQUE
    TRIM(id_rec.firstname) firstname, id_rec.middlename[1,1] middleinitial,
    TRIM(id_rec.lastname) lastname, TRIM(id_rec.suffixname) suffix,
    id_rec.id ExternalID, 'United States' as Country,
    'Carthage College' as BusinessName, 'Students' as RecordType,
    ens_rec.phone as Phone1, 'United States' as PhoneCountry1,
    TRIM(email_rec.line1) as EmailAddress1, TRIM(ens_rec.line1) ||
    TRIM(ens_rec.line2) as EmailAddress2,
    CASE WHEN NVL(ens_rec.opt_out, 1)   =   1   THEN    ens_rec.phone
                                                ELSE    ''
    END as SMS1, 'United States' as SMS1Country, 'Standing' as CustomField1,
    CASE prog_enr_rec.cl
        WHEN    'FF'    THEN    'Freshman'
        WHEN    'FN'    THEN    'Freshman'
        WHEN    'FR'    THEN    'Freshman'
        WHEN    'SO'    THEN    'Sophomore'
        WHEN    'JR'    THEN    'Junior'
        WHEN    'SR'    THEN    'Senior'
        WHEN    'GR'    THEN    'Graduate Student'
        WHEN    'UT'    THEN    'Transfer'
                        ELSE    'Bad match: ' || prog_enr_rec.cl
    END as CustomValue1, 'Dormitory' as CustomField2,
    CASE
        WHEN    UPPER(stu_serv_rec.bldg) = 'ABRD'       THEN    'Study Abroad'
        WHEN    UPPER(stu_serv_rec.bldg) = 'BW'         THEN    'Best Western'
        WHEN    UPPER(stu_serv_rec.bldg) = 'APT'        THEN    'Campus Apartments'
        WHEN    UPPER(stu_serv_rec.bldg) = 'CCHI'       THEN    'Chicago Programs'
        WHEN    UPPER(stu_serv_rec.bldg) = 'CMTR'       THEN    'Commuter'
        WHEN    UPPER(stu_serv_rec.bldg) = 'DEN'        THEN    'Denhart'
        WHEN    UPPER(stu_serv_rec.bldg) = 'JOH'        THEN    'Johnson'
        WHEN    UPPER(stu_serv_rec.bldg) = 'MADR'       THEN    'Madrigrano'
        WHEN    UPPER(stu_serv_rec.bldg[1,3]) = 'OAK'   THEN    'Oaks ' || stu_serv_rec.bldg[4,4]
        WHEN    UPPER(stu_serv_rec.bldg) = 'OFF'        THEN    'Commuter'
        WHEN    UPPER(stu_serv_rec.bldg) = 'SWE'        THEN    'Swenson'
        WHEN    UPPER(stu_serv_rec.bldg) = 'TAR'        THEN    'Tarble'
        WHEN    UPPER(stu_serv_rec.bldg) = 'TOWR'       THEN    'Tower'
        WHEN    UPPER(stu_serv_rec.bldg) = 'UN'         THEN    ''
        WHEN    UPPER(stu_serv_rec.bldg) = 'UNDE'       THEN    ''
        WHEN    UPPER(stu_serv_rec.bldg) = ''           THEN    ''
                                                        ELSE    'Bad match: ' || stu_serv_rec.bldg
    END AS CustomValue2,
    'Parking Lot' as CustomField3, --TRIM(REPLACE(lot_table.txt, 'Apts', '')) AS CustomValue3
    CASE WHEN TRIM(NVL(PLT.lot_code,'')) = 'CMTR' THEN 'CMTR' WHEN TRIM(NVL(PLT.lot_code,'')) <> '' THEN PLT.lot_code[1,3] || ' ' || PLT.lot_code[4,4] ELSE '' END AS CustomValue3
    ,'END' as END
FROM
    prog_enr_rec    INNER JOIN  id_rec              ON  prog_enr_rec.id =   id_rec.id
                    LEFT JOIN   profile_rec         ON  id_rec.id       =   profile_rec.id
                    LEFT JOIN   aa_rec as email_rec ON  id_rec.id       =   email_rec.id
                                                    AND email_rec.aa    =   "EML1"
                    LEFT JOIN   stu_acad_rec        ON  id_rec.id       =   stu_acad_rec.id
                    LEFT JOIN   aa_rec as ens_rec   ON  id_rec.id       =   ens_rec.id
                                                    AND    ens_rec.aa      =   'ENS'
                    LEFT JOIN
                    (
                        SELECT stu_serv_rec.id, MAX(stu_serv_rec.stusv_no) stusv_no
                        FROM stu_serv_rec
                        GROUP BY stu_serv_rec.id
                    )           building            ON  id_rec.id           =   building.id
                    LEFT JOIN   stu_serv_rec        ON  building.stusv_no   =   stu_serv_rec.stusv_no
                    LEFT JOIN    cc_prkg_vehicle_rec    PRK    ON    id_rec.id    =    PRK.carthage_id
                                                        AND    TODAY    BETWEEN    PRK.reg_date AND NVL(PRK.inactive_date,TODAY)
                    LEFT JOIN    cc_prkg_assign_rec    PAR    ON    PRK.veh_no    =    PAR.veh_no
                                                        AND    TODAY    BETWEEN    PAR.assign_begin AND NVL(PAR.assign_end, TODAY)
                    LEFT JOIN    cc_prkg_lot_table    PLT    ON    PAR.lot_no    =    PLT.lot_no
                    --LEFT JOIN   prkgpermt_rec   prk ON  id_rec.id           =   prk.permt_id
                    --                                AND prk.acadyr          =   YEAR(TODAY)
                    --LEFT JOIN   lot_table           ON  prk.lotcode         =   lot_table.lotcode
WHERE prog_enr_rec.subprog NOT IN
    ("YOP","UWPK","RSBD","SLS","PARA","MSW","KUSD","ENRM","CONF","CHWK")
AND prog_enr_rec.lv_date IS NULL
AND prog_enr_rec.cl IN ("FF","FN","FR","SO","JR","SR","GR","UT")
AND prog_enr_rec.acst = "GOOD"
AND stu_acad_rec.yr = YEAR(TODAY)
AND stu_acad_rec.sess IN ("RA","RC","AM","GC","PC","TC")
AND stu_acad_rec.reg_hrs > 0
ORDER BY lastname, firstname
