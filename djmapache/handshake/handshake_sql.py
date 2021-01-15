HANDSHAKE_QUERY = '''

SELECT Distinct TRIM(NVL(EML.line1,'')) AS email_address,
     TO_CHAR(PER.id) AS username,
    TRIM(CV.ldap_name) AS auth_identifier,
    '' AS card_id,  --Prox ID?  but not sure
    TRIM(IR.firstname) AS first_name,
    TRIM(IR.lastname) AS last_name,
    TRIM(IR.middlename) AS middle_name,
    TRIM(ADM.pref_name) AS preferred_name,
    -- Freshman, Sophomore, Junior, Senior, Masters, Doctorate, Postdoctoral
    -- Studies, Masters of Business Administration, Accelerated Masters,
    -- Alumni.  PA - Paralegal ND, GR - Graduate Studies, AT - ACT Cert
    -- CAN HAVE BLANKS!!
     CASE
        WHEN (CL.CL in ('FR', 'FN', 'FF')) THEN 'Freshman'  --First time frosh
                --should be pulled prior to Aug 1 of their enrollment year
           WHEN (CL.CL = 'SO') THEN 'Sophomore'
           WHEN (CL.CL = 'JR') THEN 'Junior'
           WHEN (CL.CL = 'SR') THEN 'Senior'
           WHEN (CL.CL in ('GR', 'AT')) THEN 'Masters'
           WHEN (CL.CL IN ('ND', 'SP')) THEN ''   -- What do we do with students
               --not yet classified?  Can leave blank
           WHEN (PER.acst = 'GRAD') AND (PER.lv_date IS NOT NULL
               OR PER.to_alum_date IS NOT NULL) THEN 'Alumni'
        ELSE ''
        END AS school_year_name,
       --Associates, Certificate, Advanced Certificate, Bachelors, Masters,
          --Doctorate, Postdoctoral Studies, Non-Degree Seeking.
     CASE
        WHEN (PER.deg in ('BS','BA')) THEN 'Bachelors'
        WHEN (PER.deg = 'CERT') THEN 'Certificate'
        WHEN (PER.deg in ('MBDI', 'MBA', 'MSW', 'MS', 'MM', 'MED'))
           THEN 'Masters'
        WHEN (PER.deg = 'NONE') OR (CL.CL = 'ND')
           THEN 'Non-Degree Seeking'
     ELSE ''   --    ELSE DEG.txt
        END AS education_level_name,

     SAR.cum_gpa AS cumulative_gpa,
     '' AS department_gpa,
     TRIM(MAJ1.txt) as primary_major_name,
     TRIM(MAJ1.txt) || CASE WHEN NVL(PER.major2,'') = '' THEN '' ELSE ';'
        || TRIM(MAJ2.txt) END || CASE WHEN NVL(PER.major3,'') = '' THEN ''
            ELSE ';'
        || TRIM(MAJ3.txt)
        END AS major_names,
     TRIM(NVL(MIN1.txt,'')) || CASE WHEN NVL(PER.minor2,'') = '' THEN ''
        ELSE ';'
        || TRIM(MIN2.txt) END || CASE WHEN NVL(PER.minor3,'') = '' THEN ''
        ELSE ';'
        || TRIM(MIN3.txt)
        END AS minor_names,
     '' AS college_name,
     PER.adm_date AS start_date,
    
     --Need to explicitly remove an end date if a student re-enrolls.  There is
     -- no easy way to determine which enrollees are on their second enrollment
     --Assume GRAD students were undergrads here.   Send the **CLEAR** message
     --if their new enrollment is recent.  Stop sending **CLEAR** after a
     --period of time Assume undergrads who are readmits have an acst of "READ".`
     -- Again, send the **CLEAR** for a period of time.
     --This should insure that old leave dates are erased and won't
     --send **CLEAR** for anyone else

     CASE
        WHEN PER.prog = 'GRAD' and PER.acst = 'GOOD' and PER.lv_date is null
            and PER.acad_date > TODAY-3 THEN '**CLEAR**'
        WHEN PER.prog != 'GRAD' and PER.acst = 'READ' and PER.lv_date is null
            and PER.acad_date > TODAY-3 THEN '**CLEAR**'
        ELSE TO_CHAR(PER.lv_date, '%Y-%m-%d') END
        AS end_date,
        '' as currently_attending,
        '' AS campus_name,
        '' AS opt_cpt_eligible,
        --(Optional Practical Training) and CPT (Curricular
        --Practical Training). Assigning TRUE
        '' AS ethnicity,
        '' as gender,
        'FALSE' as disabled,
     CASE WHEN AID.id IS NULL THEN 'FALSE' ELSE 'TRUE'
        END AS work_study_eligible,
        ''||TRIM(NVL(CT1.txt,''))
        ||CASE WHEN NVL(CT2.txt,'') = '' THEN ''
            ELSE ';'|| TRIM(CT2.txt) END
        ||CASE WHEN NVL(CT3.txt,'') = '' THEN ''
            ELSE ';'|| TRIM(CT3.txt) END
       	||CASE WHEN (NVL(CT1.txt,'') != '' AND NVL(SPORT.descr,'') != '')
            THEN ';'||SPORT.descr ELSE '' END
       as system_label_names,

     CASE WHEN len(REPLACE(TRIM(NVL(CELL.phone,'')), '-', '')) = 10
        THEN REPLACE(TRIM(NVL(CELL.phone,'')), '-', '')
        ELSE
     CASE WHEN len(REPLACE(TRIM(NVL(CELL.line1,'')), '-', '')) = 10
        THEN REPLACE(TRIM(NVL(CELL.line1,'')), '-', '')
        ELSE ''
        END
        END AS mobile_number,
        TRIM(NVL(ADV.line1,'')) AS assigned_to_email_address,
     CASE WHEN SPORT.descr IS NULL OR TRIM(SPORT.descr) = '' THEN 'FALSE'
        ELSE 'TRUE'
        END AS athlete,
     CASE TRIM(PRO.vet) WHEN 'N' THEN 'FALSE' WHEN 'Y' THEN 'TRUE' ELSE ''
        END AS veteran,
     TRIM(IR.city)||', '||TRIM(ST.txt)||', '||IR.ctry
        AS hometown_location_attributes,
     'FALSE' AS eu_gdpr_subject 
    
    
FROM

--select * from 
    (
    SELECT id, prog, 
         acst, subprog, deg, site, cl, adm_yr, adm_date, enr_date,
        acad_date, major1, major2, major3, adv_id, conc1, conc2, conc3,
        minor1, minor2,
        minor3, deg_grant_date, vet_ben, lv_date, to_alum, to_alum_date,
        cohort_yr, honors, tle, nurs_prog, nurs_prog_date, unmet_need
        FROM 
        (
        SELECT unique PV.id, PR.prog, PR.acst, 
            PR.subprog, PR.deg, PR.site, PR.cl, PR.adm_yr, PR.adm_date,
            PR.enr_date, PR.acad_date, PR.major1, PR.major2, PR.major3,
            adv_id, conc1, conc2, conc3, minor1, minor2, minor3,
            deg_grant_date, vet_ben, lv_date, to_alum, to_alum_date, cohort_yr,
            honors, tle, nurs_prog, nurs_prog_date, unmet_need,
            row_number() over ( partition BY PR.id
            ORDER BY
                CASE when PR.prog = 'GRAD' then 1
                    when PR.prog = 'UNDG' then 2
                    when PR.prog = 'PRDV' then 3
                    WHEN PR.PROG = 'ACT' THEN 4
                    when PR.prog = 'PARA' then 5
                    else 9 end )
                    as row_num
        FROM provisioning_vw PV
        LEFT JOIN prog_enr_rec PR
                ON PV.id = PR.id
        WHERE PV.student IN ('prog', 'stu', 'reg_clear')
            AND PR.acst IN ('GOOD' ,'LOC' ,'PROB' ,'PROC' , 'PROR' ,'READ' ,
            'RP','SAB','SHAC' ,'SHOC', 'GRAD','ACPR')
            AND (PR.subprog NOT IN ('KUSD', 'UWPK', 'YOP', 'ENRM'))
            AND (PR.CL != 'UP')
            AND (PR.lv_date IS NULL OR PR.lv_date > TODAY-15)
            AND (PR.deg_grant_date IS NULL or PR.deg_grant_date > TODAY-15)
            
        --  SCREEN OUT FIRST TIME FROSH UNTIL AUG 1
        --   Lisa Hinkley changed this to Jun 15
        --   Prior to june 15, all PREFF will be excluded
        AND    PV.ID NOT IN
            (select distinct ID from role_rec
            where role = 'PREFF' and end_date is null
        --AND TODAY < YEAR(TODAY)||'-06-20')   --For Razor
        AND TODAY < '06/12/'||YEAR(TODAY))  --for python
         --AND (PR.CL = 'SO')
            
        UNION
          
        --TO CATCH GRADS AND CHANGE THEM TO ALUMNI
        SELECT unique PR.id, 
           PR.prog, PR.acst,
           PR.subprog, PR.deg, PR.site, PR.cl, PR.adm_yr, PR.adm_date,
           PR.enr_date, PR.acad_date, PR.major1, PR.major2, PR.major3,
           adv_id, conc1, conc2, conc3, minor1, minor2, minor3,
           deg_grant_date, vet_ben, lv_date, to_alum, to_alum_date, cohort_yr,
           honors, tle, nurs_prog, nurs_prog_date, unmet_need,
           row_number() over ( partition BY PR.id
        ORDER BY
           CASE when PR.prog = 'GRAD' then 1
                when PR.prog = 'UNDG' then 2
                when PR.prog = 'PRDV' then 3
                WHEN PR.PROG = 'ACT' THEN 4
                when PR.prog = 'PARA' then 5
                else 9 end )
               as row_num
       	FROM prog_enr_rec PR
        WHERE  
           PR.acst IN ('GOOD' ,'LOC' ,'PROB' ,'PROC' , 'PROR' ,'READ' ,
           'RP','SAB','SHAC' ,'SHOC', 'GRAD','ACPR')
           AND (PR.subprog NOT IN ('KUSD', 'UWPK', 'YOP', 'ENRM'))
           AND (PR.CL != 'UP')
           AND (PR.lv_date > TODAY-90)
           AND (PR.deg_grant_date > TODAY-90)
        
           --DO NOT MARK AS ALUM IF IN ANOTHER PROGRAM
           and PR.ID not in 
              (select id from prog_enr_rec
               where deg_grant_date is null and lv_date is null )    
            
        /* UNION	
        DON'T DO THIS!!!  Currently separate process
            --TO CATCH WITHDRAWALS NO LONGER PROVISIONED
        SELECT unique PR.id, PR.prog, PR.acst,
            PR.subprog, PR.deg, PR.site, PR.cl, PR.adm_yr, PR.adm_date,
            PR.enr_date, PR.acad_date, PR.major1, PR.major2, PR.major3,
            adv_id, conc1, conc2, conc3, minor1, minor2, minor3,
            deg_grant_date, vet_ben, lv_date, to_alum, to_alum_date, cohort_yr,
            honors, tle, nurs_prog, nurs_prog_date, unmet_need,
            1  as row_num
        FROM prog_enr_rec PR
        WHERE  PR.acst IN ('WD', 'WDU')
            AND (PR.subprog NOT IN ('KUSD', 'UWPK', 'YOP', 'ENRM'))
            AND (PR.CL != 'UP')
            --AND (PR.lv_date is not null)
            AND (PR.lv_date > TODAY-60) */
             
        ) rnk_prog
        WHERE row_num = 1

    ) PER

        INNER JOIN    id_rec        IR    ON    PER.id            =    IR.id

        JOIN (SELECT id, aa, line1
            FROM aa_rec
            WHERE aa = 'EML1' AND    TODAY BETWEEN beg_date
               AND NVL(end_date, TODAY)
            ) EML ON EML.id = PER.id

        LEFT JOIN (SELECT id.id,
           replace(replace(replace(replace(replace(replace(replace(
           multiset(SELECT DISTINCT trim(a) 
              from
                  (SELECT REPLACE(invl_table.txt,"'","") a
                   FROM involve_rec
                   JOIN invl_table
                   ON invl_table.invl=involve_rec.invl
                   WHERE id=id.id
                      AND invl_table.sanc_sport = 'Y'
                   ORDER BY invl_table.txt)
                   )::lvarchar,'MULTISET{'), 'ROW'), '}'),"')",''),
                    "('",''), ',',';'), "''","'")
                   DESCR
           FROM id_rec id
           ) SPORT ON SPORT.id = PER.id

        INNER JOIN    cvid_rec CV    ON    PER.id = CV.cx_id
        LEFT JOIN st_table ST ON ST.st = IR.st
        INNER JOIN    cl_table CL    ON    PER.cl = CL.cl
        LEFT JOIN major_table MAJ1    ON    PER.major1 = MAJ1.major
        LEFT JOIN major_table MAJ2    ON    PER.major2 = MAJ2.major
        LEFT JOIN major_table MAJ3    ON    PER.major3 = MAJ3.major
        LEFT JOIN deg_table    DEG    ON    PER.deg = DEG.deg
        -- Lose 33 with adm_rec
        INNER JOIN adm_rec ADM    ON    PER.id = ADM.id
            AND ADM.prog = PER.prog
            AND    ADM.primary_app    =    'Y'
        INNER JOIN    profile_rec    PRO    ON    PER.id = PRO.id
        LEFT JOIN minor_table    MIN1  ON PER.minor1 = MIN1.minor
        LEFT JOIN minor_table    MIN2  ON PER.minor2 = MIN2.minor
        LEFT JOIN minor_table    MIN3  ON PER.minor3 = MIN3.minor

        LEFT JOIN
             (SELECT id, aa, line1
                FROM aa_rec
                WHERE aa = 'EML1' AND    TODAY BETWEEN beg_date
                AND NVL(end_date, TODAY)
                AND line1 is not null
            ) ADV on ADV.id = PER.adv_id

        LEFT JOIN
            (SELECT a.id ID, a.aa aa, a.line1 line1,
                a.phone phone, a.beg_date beg_date
            FROM aa_rec a
            INNER JOIN
                (
                SELECT id, MAX(beg_date) beg_date
                    FROM aa_rec
                    WHERE aa = 'CELL'
                    GROUP BY id
                    ) b
                ON a.id = b.id AND a.beg_date = b.beg_date
                and a.aa = 'CELL'
            ) CELL
            ON CELL.ID = PER.ID
 
           LEFT JOIN        (
            SELECT id
                    FROM aid_rec
                    WHERE aid    =    'FWSY'
                    AND stat    in    ('A','I')
                    AND TRIM(sess) || yr    IN
                        (SELECT TRIM(sess) || yr
                        FROM cursessyr_vw)
                    GROUP BY         id
                )    AID    ON PER.id = AID.id  
   
      /*   LEFT JOIN (SELECT id
           FROM aid_rec
           WHERE aid    =    'FWSY'
               AND stat    in    ('A','I')
               AND sess || yr    IN
                   (select sess||yr from acad_cal_rec
                    where beg_date < TODAY + 90
                      and end_date > TODAY -10)
               GROUP BY         id
           )    AID    ON PER.id = AID.id              */
                

        LEFT JOIN
            (SELECT id, gpa, mflag
                FROM degaudgpa_rec
                WHERE mflag = 'MAJOR1' AND gpa > 0
                ) DGR
                ON     DGR.id = PER.ID


        --This join should not be an outer join, we want to limit to only
        -- students who have registered for classes 
        -- will help keep no-shows out of the system
        -- Depending on the time of year, this can limit the numbers of
        -- students selected a great deal
        -- PREFF who are allowed into the general pool, will be screened out
        -- here until they register 
        -- BUT THIS IS BASED ON CURRENT TERM _ WOULD SCREEN OUT ALL TILL FALL
        -- Can't just use RA and RC.   Would have to use a date range based on
        -- academic  calendar or eliminate this as a restriction.
        -- SAR is only used for  GPA.   
        -- Need to redo this, find MAX ACR End date and gpa associated for each
        -- student
        
       JOIN
        (select SAR.id, SAR.cum_gpa, SAR.yr, SAR.sess, 
            max(ACR.beg_date) as latest_sess_beg_date,
            max(SAR.reg_upd_date) as MaxUpdate
            from stu_acad_rec SAR
            join (
               select prog, yr, sess, beg_date, end_date, subsess
                from acad_cal_rec
                where beg_date <= TODAY
                and end_date >= TODAY) ACR
             on ACR.yr = SAR.yr
             and ACR.sess = SAR.sess
             and nvl(ACR.subsess,"") = ""
            group by SAR.id, SAR.cum_gpa, SAR.yr, SAR.sess) SAR
            on SAR.id = PER.id
         
              
        LEFT JOIN (select conc, txt from conc_table
            WHERE LEFT(cip_no,2) in ('51')) CT1
            ON CT1.conc = PER.conc1
        LEFT JOIN (select conc, txt from conc_table
            WHERE LEFT(cip_no,2) in ('51')) CT2
            ON CT2.conc = PER.conc2
        LEFT JOIN (select conc, txt from conc_table
            WHERE LEFT(cip_no,2) in ('51')) CT3
            ON CT3.conc = PER.conc3
       
'''
