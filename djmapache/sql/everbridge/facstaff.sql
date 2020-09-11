SELECT UNIQUE
    TRIM(id_rec.firstname) firstname, id_rec.middlename[1,1] middleinitial,
    TRIM(id_rec.lastname) lastname, TRIM(id_rec.suffixname) suffix,
    id_rec.id::varchar(10) ExternalID, 'United States' as Country,
    'Carthage College' as BusinessName, 'Employee' as RecordType,
    CASE WHEN   NVL(ens_rec.opt_out, 1) =   1   THEN    ens_rec.phone
                                                ELSE    ''
    END as Phone1, 'United States' as PhoneCountry1,
    CASE WHEN   school_rec.phone    =   '___-___-____'  THEN    ''
                                                        ELSE    TRIM(school_rec.phone)
    END as Phone2, 'United States' as PhoneCountry2,
    TRIM(email_rec.line1) as EmailAddress1,
    TRIM(ens_rec.line1) || TRIM(ens_rec.line2) as EmailAddress2,
    CASE WHEN   NVL(ens_rec.opt_out, 1) =   1   THEN    TRIM(ens_rec.phone)
                                                ELSE    ''
    END as SMS1, 'United States' as SMS1Country, 'Office Building' as CustomField1,
    TRIM (CASE TRIM(UPPER(school_rec.line3[1,3]))
        WHEN    'ARE'   THEN    'Tarble Center'
        WHEN    'CC'    THEN    'Clausen Center'
        WHEN    'DIN'   THEN    ''
        WHEN    'DSC'   THEN    'David Straz Center'
        WHEN    'HL'    THEN    'Hedberg Library'
        WHEN    'JAC'   THEN    'Johnson Art Center'
        WHEN    'JOH'   THEN    'Johnson Hall'
        WHEN    'LH'    THEN    'Lentz Hall'
        WHEN    'LEN'   THEN    'Lentz Hall'
        WHEN    'MAD'   THEN    'Madrigrano Hall'
        WHEN    'PEC'   THEN    'Physical Education Center'
        WHEN    'SC'    THEN    'Siebert Chapel'
        WHEN    'SIE'   THEN    'Siebert Chapel'
        WHEN    'STR'   THEN    'David Straz Center'
        WHEN    'SU'    THEN    'Student Union'
        WHEN    'TAR'   THEN    'Tarble Center'
        WHEN    'TWC'   THEN    'Todd Wehr Center'
        WHEN    ''      THEN    ''
                        ELSE    'Bad match: ' || REPLACE(school_rec.line3,',','[comma]')
    END) as CustomValue1, 'Standing' as CustomField2,
    CASE jenzcst_rec.status_code
        WHEN    'FAC'   THEN    'Faculty'
        WHEN    'STF'   THEN    'Staff'
    END as CustomValue2, 'Full/Part Time' as CustomField3,
    CASE hrstat.hrstat
        WHEN    'FT'    THEN    'Full-Time'
        WHEN    'PT'    THEN    'Part-Time'
    END AS CustomValue3
    ,'END' as END
FROM
    id_rec  INNER JOIN  job_rec             ON  id_rec.id       =   job_rec.id
            INNER JOIN  pos_table           ON  job_rec.tpos_no =   pos_table.tpos_no
            LEFT JOIN   aa_rec  school_rec  ON  id_rec.id       =   school_rec.id
                                            AND school_rec.aa   =   "SCHL"
            LEFT JOIN   aa_rec  email_rec   ON  id_rec.id       =   email_rec.id
                                            AND email_rec.aa    =   "EML1"
            LEFT JOIN   aa_rec  ens_rec     ON  id_rec.id       =   ens_rec.id
                                            AND ens_rec.aa      =   'ENS'
            LEFT JOIN
            (
                SELECT  host_id, MIN(seq_no) seq_no
                FROM    jenzcst_rec
                WHERE   status_code IN ('FAC','STF')
                GROUP BY    host_id
            )   filter                      ON  id_rec.id       =   filter.host_id
            LEFT JOIN   jenzcst_rec         ON  filter.host_id  =   jenzcst_rec.host_id
                                            AND filter.seq_no   =   jenzcst_rec.seq_no
            LEFT JOIN
            (
                SELECT  id, hrstat
                FROM    job_rec
                WHERE   TODAY   BETWEEN beg_date    AND NVL(end_date, TODAY)
                AND     hrstat  IN      ('FT','PT')
                GROUP BY id, hrstat
            )   hrstat                      ON  id_rec.id       =   hrstat.id
WHERE
    TODAY   BETWEEN job_rec.beg_date        AND NVL(job_rec.end_date, TODAY)
    AND
    TODAY   BETWEEN pos_table.active_date   AND NVL(pos_table.inactive_date, TODAY)
    AND
    job_rec.title_rank  IS  NOT NULL
UNION
SELECT
    TRIM(id_rec.firstname) firstname, id_rec.middlename[1,1] middleinitial,
    TRIM(id_rec.lastname) lastname, TRIM(id_rec.suffixname) suffix,
    id_rec.id::varchar(10) AS ExternalID, 'United States' as Country,
    'Carthage College' as BusinessName, 'Employee' as RecordType,
    CASE WHEN   NVL(ens_rec.opt_out, 1) =   1   THEN    ens_rec.phone
                                                   ELSE    ''
    END as Phone1, 'United States' as PhoneCountry1,
    CASE WHEN   school_rec.phone    =   '___-___-____'  THEN    ''
                                                       ELSE    TRIM(school_rec.phone)
    END as Phone2, 'United States' as PhoneCountry2,
    TRIM(email_rec.line1) as EmailAddress1,
    TRIM(ens_rec.line1) || TRIM(ens_rec.line2) as EmailAddress2,
    CASE WHEN   NVL(ens_rec.opt_out, 1) =   1   THEN    TRIM(ens_rec.phone)
                                               ELSE    ''
    END as SMS1, 'United States' as SMS1Country, 'Office Building' as CustomField1,
    '' AS CustomValue1, 'Standing' as CustomField2,
    'STF' AS CustomValue2, 'Full/Part Time' as CustomField3,
    'Full-Time' AS CustomValue3, 'END' as END
FROM
    id_rec    LEFT JOIN    aa_rec    ens_rec    ON    id_rec.id        =    ens_rec.id
                                    AND    ens_rec.aa    =    'ENS'
            LEFT JOIN    aa_rec    school_rec    ON    id_rec.id    =    school_rec.id
                                        AND    school_rec.aa    =    'SCHL'
            LEFT JOIN    aa_rec    email_rec    ON    id_rec.id        =    email_rec.id
                                    AND    email_rec.aa    =    'EML1'
WHERE
    id_rec.id    =    1518708
ORDER BY lastname, firstname
