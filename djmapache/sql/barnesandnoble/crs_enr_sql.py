COURSES = '''SELECT 
         "Main" campus, TRIM(JDP.descr) school, 
         TRIM(JDP.descr) institutionDepartment, 
            
         TRIM(SMTR.sess)||' '||SMTR.yr||' '||Instructor.subsess term,
         TRIM(JDP.dept_code) Department, 
         TRIM(JCD.course_code) course, 
         TRIM(JCR.sec) SectionCode,
         'Carthage College' campusTitle, 'Carthage College' schoolTitle,	
         TRIM(JDP.descr) institutionDepartmentTitle, 	
         TRIM(JCD.title) courseTitle, 
         TRIM(JDP.dept_code)||' '||TRIM(JCR.course_code) institutionCourseCode,
         TRIM(JDP.dept_code)||' '||TRIM(JCR.course_code)||'-'||JCR.sec institutionClassCode,
            disc.disc institutionSubjectCodes, 
            disc.txt institutionSubjectsTitle, 
            TRIM(CR.crs_no)||' '||TRIM(CR.cat)||'-'||TRIM(JCR.sec)||' '||TRIM(JTR.term_code) crn,
            TRIM(st.txt)||' '||SMTR.yr||' '||CR.prog termTitle, 
        
         CASE 	WHEN trim(Instructor.subsess) = ""
        	THEN "14-Week"
        		WHEN Instructor.subsess IN ('AC', '1D', '2D', 'CT', '1G', '2G')
        	then "8-Week"
        		ELSE 
        		"7-Week"
        	END as termType, to_char(JTR.start_date, '%m/%d/%Y') termStartDate, 
            to_char(JTR.end_date, '%m/%d/%Y') termEndDate, 
            to_char(JTR.start_date, '%m/%d/%Y') sectionStartDate, 
            to_char(JTR.end_date, '%m/%d/%Y') sectionEndDate, 
            TO_CHAR(SMTR.mtg_no) classGroupId, 
            --May have to deal with crosslisted courses in separate step in Python
            Instructor.reg_num estimatedEnrollment  
        FROM 
            jenzcrs_rec JCR
        JOIN
            jenztrm_rec JTR on JTR.term_code = JCR.term_code
        AND
            --jenztrm_rec.start_date <= ADD_MONTHS(today,6)
            --AND
            JTR.end_date > TODAY
            AND right(trim(JCR.term_code),4) NOT IN ('PRDV','PARA','KUSD')
       JOIN 
            Jenzccd_rec JCD on JCD.course_code = JCR.course_code 
            AND JCD.title IS NOT NULL 
       JOIN 
            crs_rec CR on TRIM(JCR.course_code) = TRIM(CR.crs_no)||' ('||TRIM(CR.cat)||')'
       LEFT JOIN 
            jenzdpt_rec JDP on JDP.dept_code = JCD.dept_code
       JOIN 
            secmtg_rec SMTR on SMTR.crs_no = CR.crs_no
            and SMTR.sec_no = JCR.sec
            and TRIM(SMTR.sess) = left(JCR.term_code,2) 
            and SMTR.yr =  SUBSTRING(JCR.term_code FROM 4 FOR 4)
            and SMTR.cat = CR.cat
       
       JOIN 
            (select a.crs_no, a.sec_no, a.cat, a.yr, a.sess, a.subsess, 
            c.lastname as InstrName, c.firstname, c.fullname, a.fac_id, a.reg_num
            from sec_rec a, id_rec c
            where c.id = a.fac_id) Instructor
            on Instructor.sec_no = SMTR.sec_no
            and Instructor.crs_no = SMTR.crs_no
            and Instructor.cat = SMTR.cat
            and Instructor.yr = SMTR.yr
            and Instructor.sess = SMTR.sess
        JOIN sess_table st on 
            st.sess = SMTR.sess 
        JOIN disc_table disc on
            disc.dept = JDP.dept_code
    
        
   UNION 

       SELECT "Main" campus,  
        TRIM(dt.txt) school,
        TRIM(dt.txt) institutionDepartment, 
        TRIM(sr.sess)||' '||sr.yr||' '||sr.subsess term,
        TRIM(dt.dept) Department, 
        TRIM(TRIM(sr.crs_no)||' ('||TRIM(sr.cat)||')') course, 
        TRIM(sr.sec_no) SectionCode,
        'Carthage College' campusTitle, 'Carthage College' schoolTitle,	
        TRIM(dt.txt) institutionDepartmentTitle, 	
        TRIM(cr.title1)||trim(cr.title2)||trim(cr.title3) courseTitle, 
        TRIM(dt.dept) ||' '||TRIM(sr.crs_no)||' ('||TRIM(sr.cat)||')'  institutionCourseCode,
        TRIM(dt.dept) ||' '||TRIM(sr.crs_no)||'-'||TRIM(sr.sec_no)  institutionClassCode,
        disc.disc institutionSubjectCodes, 
        disc.txt institutionSubjectsTitle, 
        TRIM(cr.crs_no)||' '||TRIM(cr.cat)||'-'||TRIM(sr.sec_no)||' '||TRIM(SR.sess)||' '||TO_CHAR(sr.yr)||' '||TRIM(CR.prog) crn,
        TRIM(st.txt)||' '||sr.yr||' '||CR.prog termTitle, 
        
        CASE WHEN trim(SR.subsess) = ""
        	THEN "14-Week"
        WHEN SR.subsess IN ('AC', '1D', '2D', 'CT', '1G', '2G')
        	then "8-Week"
        ELSE 
        	"7-Week"
        	END as termType, 
        to_char(sr.beg_date, '%m/%d/%Y') termStartDate, 
        to_char(sr.end_date, '%m/%d/%Y') termEndDate, 
        to_char(sr.beg_date, '%m/%d/%Y') sectionStartDate, 
        to_char(sr.end_date, '%m/%d/%Y') sectionEndDatetartDate, 
        TO_CHAR(mtg.mtg_no)  classGroupId, 
            --May have to deal with crosslisted courses in separate step in Python
            sr.reg_num estimatedEnrollment  
            
     
            FROM 
            sec_rec sr
        JOIN 
            crs_rec cr 
         ON cr.crs_no = sr.crs_no
            and cr.cat = sr.cat
            AND sr.stat = 'X'
            AND sr.end_date > TODAY
            --AND sr.stat_date > TODAY-4
            AND trim(cr.prog) NOT IN ('PRDV','PARA','KUSD') 
        JOIN 
            id_rec ir on ir.id = sr.fac_id 
        JOIN 
            sess_table st on sr.sess = st.sess
        JOIN 
            dept_table dt on dt.dept = cr.dept
        JOIN 
            secmtg_rec mtg on mtg.crs_no = sr.crs_no
            AND mtg.sec_no = sr.sec_no
            AND trim(mtg.sess) = sr.sess 
            AND mtg.yr =  sr.yr
            AND mtg.cat = sr.cat
        JOIN disc_table disc on
            disc.dept  = dt.dept
        LEFT JOIN
            (select  b.crs_no, b.yr, b.sec_no, b.cat, b.sess, c.txt as BLDG, a.room as ROOM,
                a.mtg_no as MaxMtgNo, 
                MAX(TRIM(b.crs_no)||'-'||b.sec_no||'-'||nvl(TRIM(days)||' '||cast(beg_tm as int)||'-'||cast(end_tm as int),'------- 0-0')) as x,
                MIN(TRIM(b.crs_no)||'-'||b.sec_no||'-'||nvl(TRIM(days)||' '||cast(beg_tm as int)||'-'||cast(end_tm as int),'------- 0-0')) as y	
                FROM  secmtg_rec b
                JOIN mtg_rec a on a.mtg_no = b.mtg_no
                AND a.yr = b.yr
                AND a.sess = b.sess
                LEFT JOIN bldg_table c 
                ON c.bldg = a.bldg
            GROUP BY b.crs_no, b.yr, b.sec_no, b.cat, b.sess, c.txt, a.room, a.mtg_no ) MeetPattern
            ON MeetPattern.crs_no = sr.crs_no
            AND MeetPattern.yr = sr.yr
            AND MeetPattern.MaxMtgNo = mtg.mtg_no 
'''


USERS = '''
       SELECT DISTINCT 
        'Main' Campus,  
        'Carthage College' school,  
        TRIM(JPR.e_mail) EMAIL,
        TRIM(IR.firstname) firstname, 
        TRIM(IR.middlename) middlename, 
        TRIM(IR.lastname) lastname, 
        CASE  
        WHEN (JR.hrpay = 'VKH' and JR.hrstat in ('PTGP', 'PT'))	
            THEN 'teacher'
        WHEN (JR.hrpay = 'FVW' and JR.hrstat in ('EMER', 'FT', 'PT', 'PTGP', 
                'TLE'))	
            THEN 'teacher' 
        WHEN (JR.hrpay = 'DPW' and JR.hrstat in ('TLE'))	
            THEN 'teacher'
        WHEN (JR.hrpay = 'FVW' and JR.hrstat in ('AD', 'HR', 'HRPT', 'PATH', 'ADPT', 
                'OTH', 'PDG', 'SUM', 'PTGP', 'EMER'))	
            THEN 'administrator'
        WHEN JR.hrpay IN ('VEN', 'K97')
            THEN ("administrator")
      
        ELSE 'administrator' 
            END AS ROLE, 
        
        trim(JPR.host_username) username, IR.id ID
        
        FROM jenzcst_rec JC
            --note jenzcst_rec will return multiple values because it has a 
            --sequence number in the table
        JOIN id_rec IR ON IR.id =  JC.host_id	
            
        AND status_code not in ('PGR', '7WK', 'ALM',  'PTR', 'PFF', 'RCT', 
            'STU', 'FWS', 'CAN', 'MED', 'SUA')
           AND	JC.host_id NOT IN 
           (
            SELECT ID FROM role_rec
            WHERE role = 'PREFF' AND end_date IS NULL 
            AND MONTH(TODAY) < 8
            )  
        LEFT JOIN jenzprs_rec JPR ON JPR.host_id = JC.host_id
    
        JOIN job_rec JR on JR.id = JC.HOST_ID
            AND (JR.end_date is null or JR.end_DATE > TODAY)
            AND JR.title_rank = 1
              
     
        LEFT JOIN prog_enr_rec TLE ON TLE.id = JC.host_id
           AND TLE.acst in ('GOOD', 'GRAD')
           AND TLE.tle = 'Y'
           
           order by lastname
    '''

ENROLLMENTS = '''      SELECT 
        'Main' campus, TRIM(JDPT.descr) school, 
        TRIM(JDPT.descr) institutionDepartment, 
             TRIM(sr.sess)||' '||sr.yr||' '||sr.subsess term,
        TRIM(JDPT.dept_code) department, 
        TRIM(JCR.course_code) course, TRIM(JCR.sec) section, 
        TRIM(JPR.e_mail) email, TRIM(IR.firstname) firstName,
        TRIM(IR.middlename) middleName, TRIM(IR.lastname) lastName,
        CASE  WHEN JCP.status_code = '1PR' THEN
            "teacher"
              WHEN JCP.status_code = "STU" THEN
            "student"
         END
         userRole, 
    
         IR.id sisUserId,
         '' includedInCourseFee, '' studentFullPartTimeStatus, 
           SR.hrs creditHours
    
    FROM
        jenzcrp_rec JCP
    JOIN
        jenzcrs_rec JCR ON JCP.course_code = JCR.course_code
        AND JCP.sec = JCR.sec
        AND JCP.term_code = JCR.term_code
        and JCP.status_code = "1PR"
    JOIN
        jenztrm_rec JTRM ON JTRM.term_code = JCR.term_code   
        AND
        JTRM.end_date > TODAY
        AND
        RIGHT(TRIM(JCP.term_code),4) NOT IN ('PRDV','PARA','KUSD')
        AND to_number(JCP.host_id) NOT IN 
        (select ID from role_rec
        where role = 'PREFF' and end_date is null
        and MONTH(TODAY) < 8
       )
     JOIN
        sec_rec SR ON
        JCR.sec =  SR.sec_no
        AND TRIM(JCR.course_code) = TRIM(SR.crs_no)||' ('||TRIM(SR.cat)||')'
        AND LEFT (JCR.term_code,2) = TRIM(SR.sess)
     
    JOIN id_rec IR ON IR.id =  JCP.host_id
    JOIN jenzprs_rec JPR on JPR.host_id = JCP.host_id
    JOIN 
        Jenzccd_rec JCD on JCD.course_code = JCR.course_code 
    LEFT JOIN 
        jenzdpt_rec JDPT on JDPT.dept_code = JCD.dept_code
    
    
    UNION ALL
    SELECT
        'Main' campus, TRIM(dt.txt) school, 
        TRIM(dt.txt) institutionDepartment, 
           TRIM(sr.sess)||' '||sr.yr||' '||TRIM(sr.subsess) term, 
        TRIM(dt.dept) department, 
        TRIM(sr.crs_no)||' ('||TRIM(sr.cat)||')'  course, 
        TRIM(sr.sec_no) section, 
        TRIM(ar.line1) email, 
        TRIM(ir.firstname) firstname,
        TRIM(ir.middlename) middlename, TRIM(ir.lastname) lastname,
        "teacher" userRole, 
        ir.id sisUserId,
        '' includedInCourseFee, '' studentFullPartTimeStatus, 
        sr.hrs creditHours
    
    FROM
        sec_rec sr
    JOIN 
        crs_rec cr 
    ON cr.crs_no = sr.crs_no
        AND cr.cat = sr.cat
        AND sr.stat = 'X'
        AND sr.end_date > TODAY
        AND trim(cr.prog) NOT IN ('PRDV','PARA','KUSD') 
    JOIN 
        id_rec ir ON ir.id = sr.fac_id 
    JOIN aa_rec ar on ar.id = ir.id
        and ar.aa = 'EML1'
    JOIN 
        sess_table st ON sr.sess = st.sess
    JOIN 
        dept_table dt ON dt.dept = cr.dept
   '''
