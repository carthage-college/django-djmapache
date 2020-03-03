#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import datetime
import django
import logging
import os
import pysftp
import re
import shutil
import sys
import time
import uuid

from django.db import connections
from django.conf import settings
from djimix.core.utils import get_connection
from djimix.core.utils import xsql
from djtools.fields import TODAY
from djtools.utils.mail import send_mail


# django settings for shell environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.local')
django.setup()

# informix environment
os.environ['INFORMIXSERVER'] = settings.INFORMIXSERVER
os.environ['DBSERVERNAME'] = settings.DBSERVERNAME
os.environ['INFORMIXDIR'] = settings.INFORMIXDIR
os.environ['ODBCINI'] = settings.ODBCINI
os.environ['ONCONFIG'] = settings.ONCONFIG
os.environ['INFORMIXSQLHOSTS'] = settings.INFORMIXSQLHOSTS
os.environ['LD_LIBRARY_PATH'] = settings.LD_LIBRARY_PATH
os.environ['LD_RUN_PATH'] = settings.LD_RUN_PATH


# set up command-line options
desc = """
    Upload Common Application data to CX
"""
parser = argparse.ArgumentParser(description=desc)

parser.add_argument(
    '--test',
    action='store_true',
    help='Dry run?',
    dest='test',
)
parser.add_argument(
    '-d',
    '--database',
    help='database name.',
    dest='database',
)

# some constants
TO = settings.COMMONAPP_TO_EMAIL
FROM = settings.COMMONAPP_FROM_EMAIL
SUBJECT = '[Common Application] failed'
TEMPLATE = 'email.html'
INFORMIX_DEBUG = settings.INFORMIX_DEBUG
HEADER = '{0}\n'.format('-' * 80)

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create console handler and set level to info
phandler = logging.FileHandler('{0}commonapp.log'.format(settings.LOG_FILEPATH))
phandler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
)
phandler.setFormatter(formatter)
logger.addHandler(phandler)
# create error file handler and set level to error
phandler = logging.FileHandler('{0}commonapp_error.log'.format(
    settings.LOG_FILEPATH,
))
phandler.setLevel(logging.ERROR)
formatter = logging.Formatter(
    '%(asctime)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
)
phandler.setFormatter(formatter)
logger.addHandler(phandler)


def file_download():
    """Fetch the file from Common App file from server."""
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # External connection information for Common Application server
    xtrnl_connection = {
        'host': settings.COMMONAPP_HOST,
        'username': settings.COMMONAPP_USER,
        'password': settings.COMMONAPP_PASS,
        'cnopts': cnopts,
    }
    ###########################################################################
    # sFTP GET downloads the file from Common App file from server
    # and saves in local directory.
    ###########################################################################
    with pysftp.Connection(**xtrnl_connection) as sftp:
        # Remote Path is the Common App server and once logged in we fetch
        # directory listing
        remotepath = sftp.listdir()
        # Loop through remote path directory list
        for filename in remotepath:
            remotefile = filename
            # set local directory for which the common app file will be
            # downloaded to
            local_dir = ('{0}'.format(settings.COMMONAPP_CSV_OUTPUT))
            localpath = local_dir + remotefile
            # GET file from sFTP server and download it to localpath
            sftp.get(remotefile, localpath)
            #############################################################
            # Delete original file %m_%d_%y_%h_%i_%s_Applications(%c).txt
            # from sFTP (Common App) server
            #############################################################
            sftp.remove(filename)


def insert_exam(phile, aid, ctgry, cmpl_date, score1, score2, score3, score4, score5, score6):
    """Execute query for test scores (ACT, SAT)."""
    if cmpl_date != '':
        # creates examtmp record if there are any test scores
        try:
            q_exam = """
            INSERT INTO
                app_examtmp_rec (
                    id, ctgry, cmpl_date, self_rpt, site,
                    score1, score2, score3, score4, score5, score6
                )
            VALUES
                (
                    {0}, "{1}", TO_DATE("{2}", "%Y-%m-%d"), "Y", "CART",
                    "{3}", "{4}", "{5}", "{6}", "{7}", "{8}"
                )
            """.format(
                aid, ctgry, cmpl_date, score1, score2, score3, score4,
                score5, score6,
            )
            phile.write('{0}\n'.format(q_exam))
            logger.info('Inserted into app_examtmp_rec\n')
            connection = get_connection(earl)
            with connection:
                xsql(q_exam, connection, key=INFORMIX_DEBUG)
        except Exception:
            logger.exception()

def munge():
    # set start_time in order to see how long script takes to execute
    start_time = time.time()
    # set date and time to be added to the filename
    datetimestr = time.strftime('%Y%m%d%H%M%S')
    # initializing file counter
    file_count = 1

    # set destination path and new filename that it will be
    # renamed to when archived
    destination = ('{0}commonapp-{1}_{2}.txt'.format(
        settings.COMMONAPP_CSV_ARCHIVED,
        datetimestr,
        str(file_count),
    ))
    # renamed file name to be processed
    renamedfile = ('{0}carthage_applications.txt'.format(
        settings.COMMONAPP_CSV_OUTPUT,
    ))
    # renaming file fetched from Common App server
    # The filename comming in
    # %m_%d_%y_%h_%i_%s_Applications(%c).txt
    # The filename renamed to carthage_applications.txt
    shutil.move(localpath, renamedfile)
    # set name for the sqloutput file
    sqloutput = ('{0}/commonapp_output.sql'.format(os.getcwd()))
    # create the sql file
    with open(sqloutput, 'a') as sql_file:
        try:
            # establish mySQL database connection
            cursor = connections['admissions'].cursor()
            engine = get_engine(EARL)
            # set directory and filename where to read from
            filename=('{0}carthage_applications.txt'.format(
                settings.COMMONAPP_CSV_OUTPUT
            ))
            sql_file.write(HEADER)
            sql_file.write('-- CREATES APPLICATION FROM COMMON APP DATA\n')
            sql_file.write(HEADER)
            # open text file from CommonApp
            with open(filename, 'rb') as common_apps:
                reader = csv.DictReader(common_apps, delimiter='|')
                # set apptmp_no_list variable which is used append apptmp_no
                apptmp_no_list = []
                # set variable which is used to get count of TRAD applications
                app_TRAD_list = []
                # set variable which is used to get count of PTSM applications
                app_PTSM_list = []
                for row in reader:
                    # prints the records information for all fields
                    #print([col+'='+row[col] for col in reader.fieldnames])
                    # create UUID
                    temp_uuid = (uuid.uuid4())
                    # checks if waiver code is used which determines the
                    # payment method
                    if row['feeWaiverCode'] == '':
                        paymentMethod = 'CREDIT'
                        waiverCode = ''
                    else:
                        paymentMethod = 'WAIVER'
                        waiverCode = row['feeWaiverCode']
                    # creates apptmp record
                    try:
                        q_create_app = """
                        INSERT INTO apptmp_rec (
                            add_date, add_tm, app_source, stat, reason_txt,
                            payment_method, waiver_code
                        )
                        VALUES (
                            TODAY, TO_CHAR(CURRENT, '%H%M'), "WEBA", "H",
                            "{0}", "{1}", "{2}"
                        );
                        """.format(temp_uuid, paymentMethod, waiverCode)
                        sql_file.write(q_create_app)
                        sql_file.write('\n')
                        logger.info("Inserted into apptmp_rec");
                        do_sql(q_create_app, key=INFORMIX_DEBUG, earl=EARL)
                    except Exception:
                        logger.exception()
                    # fetch id from apptmp_no table
                    lookup_apptmp_no = '''
                    SELECT
                        apptmp_no
                    FROM
                        apptmp_rec
                    WHERE
                        reason_txt = "{0}";
                    ''' .format(temp_uuid)
                    sqlresult = do_sql(lookup_apptmp_no, earl=EARL)
                    sql_file.write(lookup_apptmp_no+'\n');
                    results = sqlresult.fetchone()
                    # sets the apptmp_no variable which is used through out
                    # the queries
                    apptmp_no = (results[0])
                    apptmp_no_list.append(str(apptmp_no));
                    sql_file.write(HEADER)
                    sql_file.write('{0} {1} {2} - {3}\n'.format(
                        '-- START INSERT NEW STUDENT APPLICATION for:',
                        row['firstName'],
                        row['lastName'],
                        str(apptmp_no),
                    ))
                    sql_file.write(HEADER)
                    logger.info('Begin Student Application: {0} {1} {2}'.format(
                        str(apptmp_no),
                        row['firstName'],
                        row['lastName']),
                    )
                    # fetch id from app_voucher on mySQL dB (admissions)
                    # insert into app_vouchers_users on mySQL dB
                    if row['feeWaiverCode'] != '':
                        try:
                            q_match = """
                                SELECT
                                    id
                                FROM
                                    app_vouchers
                                WHERE
                                    NOW() < expiration
                                AND
                                    REPLACE(code,"-","") = "{0}"
                            """ .format(row['feeWaiverCode'].replace('-', ''))
                            sql_file.write(q_match+'\n');
                            cursor.execute(q_match)
                            voucher_result = cursor.fetchone()
                        except Exception:
                            logger.exception()
                        # if no results are returned set voucher_id to zero
                        if voucher_result == None:
                            voucher_id = 0
                        else:
                            # if results are returned set voucher_id to result
                            voucher_id = (voucher_result[0])
                            # inserts voucher id into app_voucher_users
                            try:
                                q_update_voucher = '''
                                INSERT INTO app_voucher_users (voucher_id, app_id, submitted_on)
                                VALUES ({0}, {1}, NOW())
                                ''' .format(voucher_id, apptmp_no)
                                sql_file.write(q_update_voucher+'\n');
                                logger.info("Inserted into app_voucher_users"+'\n');
                                cursor.execute(q_update_voucher)
                            except Exception:
                                logger.exception()
                    sql_file.write("--There were no waiver codes used for this application"+'\n');
                    # creates application temp record
                    try:
                        q_create_id = '''
                        INSERT INTO app_idtmp_rec
                        (id, firstname, lastname, suffixname, cc_username, cc_password, addr_line1, addr_line2, city, st, zip, ctry, phone, ss_no,
                        middlename, aa, add_date, ofc_add_by, upd_date, purge_date, prsp_no, name_sndx, correct_addr, decsd, valid)
                        VALUES ({0}, "{1}", "{2}", "{3}", "{4}", "{0}", "{5}", "{6}", "{7}", "{8}", "{9}", "{10}", "{11}", "{12}", "{13}", "PERM",
                        TODAY, "ADMS", TODAY, TODAY + 2 UNITS YEAR, "0", "", "Y", "N", "Y");
                        ''' .format(apptmp_no, row['firstName'], row['lastName'], row['suffix'], row['emailAddress'], re.sub('\W+', ' ', row['permanentAddress1']),
                                re.sub('\W+', ' ', row['permanentAddress2']), row['permanentAddressCity'], row['permanentAddressState'], row['permanentAddressZip'],
                                row['permanentAddressCountry'], row['preferredPhoneNumber'].replace('+1.', ''), row['ssn'], row['middleName'])
                        sql_file.write(q_create_id+'\n');
                        logger.info("Inserted into app_idtmp_rec"+'\n');
                        do_sql(q_create_id, key=INFORMIX_DEBUG, earl=EARL)
                    except Exception:
                        logger.exception()
                    ##################################################################################
                    # The Y/N value of contactConsent may seem a little backwards intuitively.
                    # Y = The student has opted out meaning Carthage does NOT have permission to text
                    # N = The student has opted in meaning Carthage does have permission to text
                    #################################################################################
                    ################################################
                    # BEGIN - preferred phone for student
                    ################################################
                    if row['preferredPhone'] == 'Mobile':
                        if row['contactConsent'] == 'Y':
                            contactConsent = 'N'
                        elif row['contactConsent'] == 'N':
                            contactConsent = 'Y'
                        # preferred phone is a Mobile
                        try:
                            q_insert_aa_cell = '''
                            INSERT INTO app_aatmp_rec
                            (id, aa, beg_date, phone, opt_out)
                            VALUES ({0}, "CELL", TODAY, "{1}", "{2}");
                            ''' .format(apptmp_no, row['preferredPhoneNumber'].replace('+1.', ''), row['contactConsent'])
                            sql_file.write(q_insert_aa_cell+'\n');
                            logger.info("Inserted into app_aatmp_rec"+'\n');
                            do_sql(q_insert_aa_cell, key=INFORMIX_DEBUG, earl=EARL)
                        except Exception:
                            logger.exception()
                    ################################################
                    # BEGIN - alternate phone available for student
                    ################################################
                    if row['alternatePhoneAvailable'] != '' and row['alternatePhoneAvailable'] != 'N':
                        altType = 'CELL'
                        if row['contactConsent'] == 'Y':
                            contactConsent = 'N'
                        elif row['contactConsent'] == 'N':
                            contactConsent = 'Y'
                        if row['alternatePhoneAvailable'] == 'Home':
                            altType = 'HOME'
                        # alternate phone is available
                        try:
                            q_insert_aa_cell = '''
                            INSERT INTO app_aatmp_rec
                            (id, aa, beg_date, phone, opt_out)
                            VALUES ({0}, "{1}", TODAY, "{2}", "{3}");
                            ''' .format(apptmp_no, altType, row["alternatePhoneNumber"].replace('+1.', ''), row["contactConsent"])
                            sql_file.write(q_insert_aa_cell+'\n');
                            logger.info("Inserted into app_aatmp_rec"+'\n');
                            do_sql(q_insert_aa_cell, key=INFORMIX_DEBUG, earl=EARL)
                        except Exception:
                            logger.exception()
                    # creates application site record
                    try:
                        q_create_site = '''
                        INSERT INTO app_sitetmp_rec
                        (id, home, site, beg_date)
                        VALUES ({0}, "Y", "CART", TODAY);
                        ''' .format(apptmp_no)
                        sql_file.write(q_create_site+'\n');
                        logger.info("Inserted into app_sitetmp_rec"+'\n');
                        do_sql(q_create_site, key=INFORMIX_DEBUG, earl=EARL)
                    except Exception:
                        logger.exception()
                    # determine the type of studentStatus and set studentStatus and Hours Enrolled
                    if row['studentStatus'] == 'Full Time':
                        studentStatus = 'TRAD'
                        intendHoursEnrolled = 16
                        app_TRAD_list.append(str(apptmp_no))
                    elif row['studentStatus'] == 'Part Time':
                        studentStatus = 'TRAD'
                        intendHoursEnrolled = 16
                        app_PTSM_list.append(str(apptmp_no))
                    ###############################################
                    # Adjust the code for Common App
                    # to make any app that comes in through
                    # Common App full time
                    # even if they indicate part time on their
                    # Common App
                    ###############################################
                    """
                    elif row['studentStatus'] == 'Part Time':
                        studentStatus = 'PTSM'
                        intendHoursEnrolled = 4
                    """
                    # fetch preferredStartTerm from Common App data ex.(Fall 2018, Spring 2018, J-Term 2018)
                    preferredStartTerm = row['preferredStartTerm']
                    # spliting preferredStartTerm
                    planArray = preferredStartTerm.split(' ')
                    # set planEnrollYear to Year
                    planEnrollYear = planArray[1]
                    # create school session dictionary
                    session = {
                        'Fall': 'RA',
                        'J-Term': 'RB',
                        'Spring': 'RC',
                    }
                    # create planEnrollSession from value in dictionary
                    planEnrollSession = session[planArray[0]]
                    # Any nursing majors (1, 2, 3) need to drive the studentType
                    # determine the studentType
                    if row['studentType'] == 'FY' and row['freshmanNursing'] == 'Yes':
                        studentType = 'FN'
                        transfer = 'N'
                    elif row['studentType'] == 'FY':
                        studentType = 'FF'
                        transfer = 'N'
                    elif row['studentType'] == 'TR':
                        studentType = 'UT'
                        transfer = 'Y'
                    # replacing first part of Common App code for major
                    major1 = row['major1'].replace('ADM-MAJOR-', '').strip()
                    major2 = row['major2'].replace('ADM-MAJOR-', '').strip()
                    major3 = row['major3'].replace('ADM-MAJOR-', '').strip()
                    # replacing first part of Common App code for preferred residence
                    hsgType = row['preferredResidence'].replace('ADM-HSG_TYPE-', '').strip()
                    # set armedForcesStatus variables
                    if row['armedForcesStatus'] == 'Currently_serving':
                        armedForcesStatus = 'Y'
                    elif row['armedForcesStatus'] == 'Previously_served':
                        armedForcesStatus = 'Y'
                    elif row['armedForcesStatus'] == 'Current_Dependent':
                        armedForcesStatus = 'Y'
                    else:
                        armedForcesStatus = 'N'
                    # creating Parent Marital Status dictionary
                    parentMtlStat = {
                        'Married': 'M',
                        'Separated': 'T',
                        'Divorced': 'D',
                        'Widowed': 'W',
                        'Never Married': 'S',
                    }
                    try:
                        parnt_mtlstat = parentMtlStat[
                            row['parentsMaritalStatus']
                        ]
                    except KeyError:
                        parnt_mtlstat = 'O'
                    parent1 = ''
                    parent2 = ''
                    # determine which Parent Type coming from Common App is Father or Mother
                    if row['parent1Type'] == 'Father':
                        parent1 = 'F'
                    if row['parent1Type'] == 'Mother':
                        parent1 = 'M'
                    if row['parent2Type'] == 'Mother':
                        parent2 = 'M'
                    if row['parent2Type'] == 'Father':
                        parent2 = 'F'
                    # creating Living With dictionary
                    liveWith = {
                        'Both Parents': 'B',
                        'Parent 1': parent1,
                        'Parent 2': parent2,
                        'Legal Guardian': 'G',
                        'Other': 'O',
                        'Ward of the Court/State': 'O'
                    }
                    otherLivingSituation = ''
                    # create variables for Lived with based on the dictionary
                    try:
                        live_with = liveWith[row['permanentHome']]
                        if live_with == 'O':
                            otherLivingSituation = row['otherLivingSituation']
                    except KeyError:
                        live_with = 'O'
                    # creates admtmp record
                    try:
                        q_create_adm = '''
                        INSERT INTO app_admtmp_rec (
                            id, primary_app, plan_enr_sess, plan_enr_yr,
                            intend_hrs_enr, trnsfr, cl, add_date,
                            parent_contr, enrstat, rank, wisconsin_coven,
                            emailaddr, prog, subprog, upd_date, act_choice,
                            stuint_wt, jics_candidate, major, major2, major3,
                            app_source, pref_name, discipline, parnt_mtlstat,
                            live_with, live_with_other, vet_ben, model_score,
                            hsg_type
                        ) VALUES (
                            {0}, "Y", "{1}", {2}, "{3}", "{4}", "{5}", TODAY,
                            "0.00", "", "0", "", "{6}", "UNDG", "{7}", TODAY,
                            "", "0", "N", "{8}", "{9}", "{10}", "C", "{11}",
                            "{12}", "{13}", "{14}", "{15}", "{16}", 0, "{17}"
                        );
                        '''.format(
                            apptmp_no, planEnrollSession, planEnrollYear,
                            intendHoursEnrolled, transfer, studentType,
                            row['emailAddress'], studentStatus,
                            major1, major2, major3, row['preferredName'],
                            row['schoolDiscipline'], parnt_mtlstat,
                            live_with, otherLivingSituation, armedForcesStatus,
                            hsgType,
                        )
                        sql_file.write(q_create_adm+'\n')
                        logger.info("Inserted into app_admtmp_rec"+'\n')
                        do_sql(q_create_adm, key=INFORMIX_DEBUG, earl=EARL)
                    except Exception:
                        logger.exception()
                    # if there is Displinary reasons they will be added
                    if row['schoolDiscipline'] != '':
                        if row['schoolDiscipline'] == 'Y':
                            try:
                                resource = 'DISMISS'
                                q_insertText = '''
                                INSERT INTO app_ectctmp_rec
                                (id, tick, add_date, resrc, stat, txt)
                                VALUES (?, ?, ?, ?, ?, ?);
                                '''
                                sql_file.write(q_insertText+'\n')
                                logger.info("""
                                    Inserted into app_ectctmp_rec for
                                    disciplinary explanation\n
                                """)
                                engine.execute(
                                    q_insertText,
                                    [apptmp_no, 'ADM', TODAY, resource, 'C', reasontxt]
                                )
                            except Exception:
                                logger.exception()
                    ################################################
                    # BEGIN - alternate address for student
                    ################################################
                    if row['alternateAddressAvailable'] == 'Y':
                        # creates aatmp record if alternate address is Y
                        try:
                            q_insert_aa_mail = '''
                            INSERT INTO app_aatmp_rec
                            (line1, line2, city, st, zip, ctry, id, aa, beg_date)
                            VALUES ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", {6}, "MAIL", TODAY);
                            ''' .format(row['currentAddress1'], row['currentAddress2'], row['currentAddressCity'],
                                        row['currentAddressState'], row['currentAddressZip'], row['currentAddressCountry'], apptmp_no)
                            sql_file.write(q_insert_aa_mail)
                            logger.info("Inserted into app_aatmp_rec"+'\n')
                            do_sql(q_insert_aa_mail, key=INFORMIX_DEBUG, earl=EARL)
                        except Exception:
                            logger.exception()
                    else:
                        sql_file.write('--There were no alternate addresses for this application.\n\n');
                    ################################################
                    # BEGIN - school(s) attended for a student
                    ################################################
                    if row['schoolLookupCeebCode'] != '' and row['schoolLookupCeebName'] != '':
                        if row['graduationDate'] == '':
                            graduationDate = ''
                        else: # formatting the graduationDate
                            graduationDate = datetime.datetime.strptime(row['graduationDate'], '%m/%Y').strftime('%Y-%m-01')
                        if row['entryDate'] == '':
                            entryDate = ''
                        else: # formatting the entryDate
                            entryDate = datetime.datetime.strptime(row['entryDate'], '%m/%Y').strftime('%Y-%m-01')
                        if row['exitDate'] == '':
                            exitDate = ''
                        else: # formatting the exitDate
                            exitDate = datetime.datetime.strptime(row['exitDate'], '%m/%Y').strftime('%Y-%m-01')
                        # creates edtmp record attended by the student
                        try:
                            q_create_school = '''
                            INSERT INTO app_edtmp_rec
                            (id, ceeb, fullname, city, st, grad_date, enr_date, dep_date, stu_id, sch_id, app_reltmp_no, rel_id, priority, zip, aa, ctgry, acad_trans)
                            VALUES ({0}, {1}, "{2}", "{3}", "{4}", TO_DATE("{5}", "%Y-%m-%d"), TO_DATE("{6}", "%Y-%m-%d"), TO_DATE("{7}", "%Y-%m-%d"), 0, 0, 0, 0, 0, "{8}", "hs", "HS", "N");
                        ''' .format(apptmp_no, row['schoolLookupCeebCode'], row['schoolLookupCeebName'], row['schoolLookupCity'], row['schoolLookupState'], graduationDate,
                                    entryDate, exitDate, row['schoolLookupZip'])
                            sql_file.write(q_create_school)
                            sql_file.write('--Executing create school qry')
                            sql_file.write('\n\n')
                            logger.info("Inserted into app_edtmp_rec")
                            do_sql(q_create_school, key=INFORMIX_DEBUG, earl=EARL)
                        except Exception:
                            logger.exception()
                    ################################################
                    # BEGIN - other school(s) attended for a student
                    ################################################
                    if row['otherSchoolNumber'] != '' and int(row['otherSchoolNumber']) > 0:
                        for schoolNumber in range(2, int(row['otherSchoolNumber'])+1):
                            # check to see that there is a CeebCode coming from Common App
                            if row['secondarySchool'+str(schoolNumber)+'CeebCode'] == '':
                                secondarySchoolCeebCode = 0
                            else:
                                secondarySchoolCeebCode = row['secondarySchool'+str(schoolNumber)+'CeebCode']
                            if row['secondarySchool'+str(schoolNumber)+'FromDate'] == '':
                                fromDate = ''
                            else: # formatting the fromDate
                                fromDate = datetime.datetime.strptime(row['secondarySchool'+str(schoolNumber)+'FromDate'], '%m/%Y').strftime('%Y-%m-01')
                            if row['secondarySchool'+str(schoolNumber)+'ToDate'] == '':
                                toDate = ''
                            else: # formatting the toDate
                                toDate = datetime.datetime.strptime(row['secondarySchool'+str(schoolNumber)+'ToDate'], '%m/%Y').strftime('%Y-%m-01')
                            # creates edtmp record if there are any secondary schools
                            try:
                                q_create_other_school = '''
                                INSERT INTO app_edtmp_rec
                                (id, ceeb, fullname, city, st, grad_date, enr_date, dep_date, stu_id, sch_id, app_reltmp_no, rel_id, priority, zip, aa, ctgry, acad_trans)
                                VALUES ({0}, {1}, "{2}", "{3}", "{4}", "", TO_DATE("{5}", "%Y-%m-%d"), TO_DATE("{6}", "%Y-%m-%d"), 0, 0, 0, 0, 0, "{7}", "hs", "HS", "N");
                            ''' .format(apptmp_no, secondarySchoolCeebCode, row['secondarySchool'+str(schoolNumber)+'CeebName'], row['secondarySchool'+str(schoolNumber)+'City'],
                                        row['secondarySchool'+str(schoolNumber)+'State'], fromDate, toDate, row['secondarySchool'+str(schoolNumber)+'Zip'])
                                sql_file.write(q_create_other_school+'\n\n')
                                sql_file.write('--Executing other school qry')
                                sql_file.write('\n\n')
                                logger.info("""
                                    Inserted into app_edtmp_rec for other
                                    secondary school
                                """)
                                do_sql(q_create_other_school, key=INFORMIX_DEBUG, earl=EARL)
                            except Exception:
                                logger.exception()
                    else:
                        sql_file.write('--There were no other schools attended')
                        sql_file.write('--for this application.')
                        sql_file.write('\n\n')
                    ###############################################
                    # BEGIN - relatives attended Carthage
                    ###############################################
                    if row['relativesAttended'] == 'Yes':
                        for relativeNumber in range (1, 5 +1):
                            if row['relative'+str(relativeNumber)+'FirstName'] != '':
                                relativeGradYear = row['relative'+str(relativeNumber)+'GradYear1']
                                if relativeGradYear == '':
                                    relativeGradYear = 0
                                # creates reltmp record if there are any relatives
                                try:
                                    q_alumni = '''
                                    INSERT INTO app_reltmp_rec (id, rel_id, rel, fullname, phone_ext, aa, zip)
                                    VALUES ({0}, 0, 5, "{1}", {2}, "ALUM", 0);
                                ''' .format(apptmp_no, row['relative'+str(relativeNumber)+'FirstName'] + ' ' + row['relative'+str(relativeNumber)+'LastName'],
                                    relativeGradYear)
                                    sql_file.write(q_alumni+'\n\n');
                                    logger.info("""
                                        Inserted into app_reltmp_rec for
                                        Alumni
                                    """)
                                    do_sql(q_alumni, key=INFORMIX_DEBUG, earl=EARL)
                                except Exception:
                                    logger.exception()
                    else:
                        sql_file.write('--There were no relatives (ALUMI)')
                        sql_file.write('--for this application.\n\n')
                    ###############################################
                    # BEGIN - siblings **if there are no siblings
                    # then nothing is inserted
                    ###############################################
                    if row['numberOfSiblings'] > 0:
                        # set dictionary for sibling education level
                        educationLevel = {
                            'None': 'None',
                            'Some grade school': 'Elem',
                            'Completed grade school': 'HS',
                            'Some secondary school': 'HS',
                            'Graduated from secondary school': 'HS',
                            'Some trade school or community college': 'Juco',
                            'Graduated from trade school or community college': 'Juco',
                            'Some college': 'Coll',
                            'Graduated from college': 'Bach',
                            'Graduate school': 'Mast',
                        }
                        for siblingNumber in range (1, 5 +1):
                            if row['sibling'+str(siblingNumber)+'FirstName'] != '':
                                # creates reltmp record if there are any siblings
                                try:
                                    q_sibing_name = '''
                                    INSERT INTO app_reltmp_rec (id, rel_id, rel, fullname, phone_ext, aa, zip, prim, addr_line2, suffix)
                                    VALUES ({0}, 0, "SIB", "{1}", "{2}", "SBSB", 0, "Y", "{3}", "{4}");
                                ''' .format(apptmp_no, row['sibling'+str(siblingNumber)+'FirstName'] + ' ' + row['sibling'+str(siblingNumber)+'LastName'],
                                    row['sibling'+str(siblingNumber)+'Age'], row['sibling'+str(siblingNumber)+'CollegeCeebName'], educationLevel[row['sibling'+str(siblingNumber)+'EducationLevel']])
                                    sql_file.write(q_sibing_name+'\n\n');
                                    logger.info("""
                                        Inserted into app_reltmp_rec
                                    """)
                                    do_sql(q_sibing_name, key=INFORMIX_DEBUG, earl=EARL)
                                except Exception:
                                    logger.exception()
                    else:
                        sql_file.write('--There were no siblings for this application.\n\n');
                    ###############################################
                    # BEGIN - parent(s), legal guardian
                    ###############################################
                    fatherIndex = 1
                    motherIndex = 2
                    if row['parent1Type'] == 'Mother':
                        fatherIndex = 2
                        motherIndex = 1
                    # creates partmp record if there are any parents
                    try:
                        q_insert_partmp_rec = '''
                        INSERT INTO partmp_rec (
                            id, app_no, f_first_name, f_last_name, f_addr_line1,
                            f_addr_line2, f_city, f_st, f_zip, f_ctry, f_college,
                            f_deg_earn, f_title, f_suffix, f_email, f_phone, f_job,
                            f_employer, m_first_name, m_last_name, m_addr_line1,
                            m_addr_line2, m_city, m_st, m_zip, m_ctry, m_college,
                            m_deg_earn, m_title, m_suffix, m_email, m_phone, m_job,
                            m_employer, g_first_name, g_last_name, g_addr_line1,
                            g_addr_line2, g_city, g_st, g_zip, g_ctry, g_college,
                            g_deg_earn, g_title, g_suffix, g_email, g_phone,
                            g_job, g_employer
                        ) VALUES (
                            0, {0}, "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}",
                            "{8}", "{9}", "{10}", "{11}", "{12}", "{13}", "{14}",
                            "{15}", "{16}", "{17}", "{18}", "{19}", "{20}", "{21}",
                            "{22}", "{23}", "{24}", "{25}", "{26}", "{27}", "{28}",
                            "{29}", "{30}", "{31}", "{32}", "{33}", "{34}", "{35}",
                            "{36}", "{37}", "{38}", "{39}", "{40}", "{41}", "{42}",
                            "{43}", "{44}", "{45}", "{46}", "{47}", "{48}"
                        );'''.format(
                            apptmp_no,
                            # father
                            row['parent'+str(fatherIndex)+'FirstName'],
                            row['parent'+str(fatherIndex)+'LastName'],
                            row['parent'+str(fatherIndex)+'Address1'],
                            row['parent'+str(fatherIndex)+'Address2'],
                            row['parent'+str(fatherIndex)+'AddressCity'],
                            row['parent'+str(fatherIndex)+'AddressState'],
                            row['parent'+str(fatherIndex)+'AddressZip'],
                            row['parent'+str(fatherIndex)+'AddressCountry'],
                            row['parent'+str(fatherIndex)+'College1NameCeebName'],
                            row['parent'+str(fatherIndex)+'College1Degree1'],
                            row['parent'+str(fatherIndex)+'Title'],
                            row['parent'+str(fatherIndex)+'Suffix'],
                            row['parent'+str(fatherIndex)+'Email'],
                            row['parent'+str(fatherIndex)+'Phone'].replace('+1.', ''),
                            row['parent'+str(fatherIndex)+'Occupation'],
                            row['parent'+str(fatherIndex)+'Employer'],
                            # mother
                            row['parent'+str(motherIndex)+'FirstName'],
                            row['parent'+str(motherIndex)+'LastName'],
                            row['parent'+str(motherIndex)+'Address1'],
                            row['parent'+str(motherIndex)+'Address2'],
                            row['parent'+str(motherIndex)+'AddressCity'],
                            row['parent'+str(motherIndex)+'AddressState'],
                            row['parent'+str(motherIndex)+'AddressZip'],
                            row['parent'+str(motherIndex)+'AddressCountry'],
                            row['parent'+str(motherIndex)+'College1NameCeebName'],
                            row['parent'+str(motherIndex)+'College1Degree1'],
                            row['parent'+str(motherIndex)+'Title'],
                            row['parent'+str(motherIndex)+'Suffix'],
                            row['parent'+str(motherIndex)+'Email'],
                            row['parent'+str(motherIndex)+'Phone'].replace('+1.', ''),
                            row['parent'+str(motherIndex)+'Occupation'],
                            row['parent'+str(motherIndex)+'Employer'],
                            # legal guardian
                            row['legalGuardianFirstName'], row['legalGuardianLastName'],
                            row['legalGuardianAddress1'], row['legalGuardianAddress2'],
                            row['legalGuardianAddressCity'], row['legalGuardianAddressState'],
                            row['legalGuardianAddressZip'], row['legalGuardianAddressCountry'],
                            row['legalGuardianCollege1NameCeebName'],
                            row['legalGuardianCollege1Degree1'],
                            row['legalGuardianTitle'], row['legalGuardianSuffix'],
                            row['legalGuardianEmail'],
                            row['legalGuardianPhone'].replace('+1.', ''),
                            row['legalGuardianOccupation'],
                            row['legalGuardianEmployer'],
                        )
                        sql_file.write(q_insert_partmp_rec+'\n')
                        logger.info("""
                            Inserted into partmp_rec
                        """)
                        do_sql(q_insert_partmp_rec, key=INFORMIX_DEBUG, earl=EARL)
                    except Exception:
                        logger.exception()
                    ###############################################
                    # BEGIN - activities
                    ###############################################
                    if row['activity1'] != '':
                        for activityNumber in range (1, 5 +1):
                            # replacing first part of Common App code for activity
                            activity = row['activity'+str(activityNumber)].replace("INTERESTS-INTEREST-", "")
                            if activity:
                                # creates inttmp record if there are any activities
                                try:
                                    insert_interests = '''
                                    INSERT INTO app_inttmp_rec (id, prsp_no, interest, ctgry, cclevel)
                                    VALUES ({0}, 0, "{1}", "", "Y");
                                ''' .format(apptmp_no, activity)
                                    sql_file.write(insert_interests+'\n');
                                    logger.info("""
                                        Inserted into app_inttmp_rec
                                    """)
                                    do_sql(insert_interests, key=INFORMIX_DEBUG, earl=EARL)
                                except Exception:
                                    logger.exception()
                    else:
                        sql_file.write(
                            """
                            --There were no activities for this application.\n\n
                        """)
                    ###############################################
                    # BEGIN - ethnic backgrounds
                    ###############################################
                    # removing space when there are multiple ethnic backgrounds
                    background = (row['background'].replace(' ', ''))
                    # creating array
                    array_ethnic = background.split(',')
                    converted = []
                    # create ethnicity dictionary
                    ethnicity = {
                        'N': 'AM',
                        'A': 'AS',
                        'B': 'BL',
                        'P': 'IS',
                        'W': 'WH'
                    }
                    # Loop through array comparing ethnicity(key)
                    # setting it to ethnicity(value)
                    for eth in array_ethnic:
                        try:
                            converted.append(ethnicity[eth])
                        except:
                            pass
                    # setting ethnic_code
                    if len(converted) == 1:
                        ethnic_code = converted[0]
                    elif len(converted) == 0:
                        ethnic_code = 'UN'
                    else:
                        ethnic_code = 'MU'
                    if len(converted) > 1:
                        for eth_race in converted:
                            # creates mracetmp record if there are
                            # multiple ethnic codes
                            try:
                                insert_races = '''
                                INSERT INTO app_mracetmp_rec
                                (id, race)
                                VALUES ({0}, "{1}");
                                ''' .format(apptmp_no, eth_race)
                                sql_file.write(insert_races+'\n');
                                logger.info("""
                                    Inserted into app_mracetmp_rec
                                """)
                                do_sql(insert_races, key=INFORMIX_DEBUG, earl=EARL)
                            except Exception:
                                logger.exception()
                    else:
                        sql_file.write('--There was nothing to insert into the mracetmp table.\n\n');
                    # formatting the dateOfBirth
                    dateOfBirth = datetime.datetime.strptime(row['dateOfBirth'], '%m/%d/%Y').strftime('%Y-%m-%d')
                    # create religious denomination codes dictionary
                    denomination = {
                        'BAP': 'BA',
                        'CGR': 'CO',
                        'HIN': 'HI',
                        'HBR': 'JE',
                        'LUT': 'LO',
                        'MET': 'ME',
                        'MEN': 'MN',
                        'MUS': 'MU',
                        'OTH': 'O',
                        'PRB': 'PR',
                        'CAT': 'RC',
                        '': ''
                    }
                    # create variables for the religious preference
                    # based on the dictionary
                    try:
                        religiousPreference = denomination[
                            row['religiousPreference']
                        ]
                    except KeyError:
                        religiousPreference = 'O'
                    # creates proftmp record
                    try:
                        q_create_prof = '''
                        INSERT INTO app_proftmp_rec (id, birth_date, church_id, prof_last_upd_date, sex, birthplace_city, birthplace_st,
                        birthplace_ctry, visa_code, citz, res_st, res_cty, race, hispanic, denom_code, vet)
                        VALUES ({0}, TO_DATE("{1}", "%Y-%m-%d"), 0, TODAY, "{2}", "{3}", "{4}", "{5}", "", "{6}", "", "", "{7}", "{8}",
                        "{9}", "{10}");
                        ''' .format(apptmp_no, dateOfBirth, row['sex'], row['birthCity'], row['birthState'], row['birthCountry'], row['citizenships'],
                        ethnic_code, row['hispanicLatino'], religiousPreference, armedForcesStatus)
                        sql_file.write(q_create_prof+'\n');
                        logger.info("""
                            Inserted into app_proftmp_rec
                        """)
                        do_sql(q_create_prof, key=INFORMIX_DEBUG, earl=EARL)
                    except Exception:
                        logger.exception()
                    ###############################################
                    # BEGIN - testing scores
                    # testing scores array for ACT, SAT_New
                    # insert_exam() creates the insert statement
                    ###############################################
                    if row['totalTestsTaken'] != '':
                        userTests = row['totalTestsTaken'].split(',')
                        for t in userTests:
                            if t.strip() == 'ACT' and row['actCompositeDate'] != '':
                                cmpl_date = datetime.datetime.strptime(
                                    row['actCompositeDate'], '%m/%d/%Y',
                                ).strftime('%Y-%m-%d')
                                insert_exam(sql_file, apptmp_no, 'ACT', cmpl_date, row['actCompositeScore'], row['actEnglishScore'], row['actMathScore'],
                                    row['actReadingScore'], row['actScienceScore'], row['actWritingScore'])
                            elif t.strip() == 'SAT_New' and row['satRWDate'] != '':
                                cmpl_date = datetime.datetime.strptime(row['satRWDate'], '%m/%d/%Y').strftime('%Y-%m-%d')
                                insert_exam(sql_file, apptmp_no, 'SAT', cmpl_date, '', row['satRWScore'], row['satMathScore'], row['satEssayScore'], '', '')
                    else:
                        sql_file.write('--There were no tests for this application.\n\n');
                    sql_file.write(HEADER)
                    sql_file.write('-- END INSERT NEW STUDENT APPLICATION for: ' + row['firstName'] + ' ' + row['lastName'] + '\n')
                    logger.info('Complete Student Application:')
                    logger.info(
                        str(apptmp_no),
                        row['firstName'],
                        row['lastName'],
                        studentStatus,
                    )
                sql_file.write('-- STUDENT IDs: {0}\n'.format(
                    str(apptmp_no_list),
                ))
                apps_count = len(apptmp_no_list)
                logger.info('Number of Applications:')
                logger.info(apps_count)
                # Display current date
                print('Date: {0}'.format(time.strftime('%A, %B %d %Y')))
                print('Number of Applications: {0}'.format(apps_count))
                TRAD_count = len(app_TRAD_list)
                print('TRAD: {0}'.format(TRAD_count))
                logger.info('Number of TRAD Applicants:')
                logger.info(TRAD_count)
                PTSM_count = len(app_PTSM_list)
                print('PTSM: {0}'.format(PTSM_count))
                logger.info('Number of PTSM Applicants:')
                logger.info(PTSM_count)
                # output of how long it takes to run script
                print("--- {0} seconds ---".format((time.time() - start_time)))
        except Exception:
            logger.exception()
        # rename the archive file
        # renames carthage_applications.txt to
        # commonapp-%Y%m%d%H%M%S.txt
        shutil.move(renamedfile, destination)
        file_count += 1


def main():
    """Unusually long and far too complext main function."""
    # execute sftp code that needs to be executed in production only
    if not test:
        file_download()
    # set local path and list files
    localpath = os.listdir(settings.COMMONAPP_CSV_OUTPUT)
    if localpath:
        for localfile in localpath:
            localpath = settings.COMMONAPP_CSV_OUTPUT + localfile
            file_size = os.stat(localpath).st_size
            if localfile.endswith(".txt"):
                if file_size > 0:
                    munge()
                else:
                    # email the filesize is 0 there is no data in the file
                    body = 'File {0} was found but filesize is {1}'.format(
                        localfile, file_size,
                    )
                    send_mail(None, TO, SUBJECT, FROM, TEMPLATE, body)
                    logger.error(body)
            else:
                # found file but the extension does not end in .txt
                body = """
                    File {0} was found but extension does not end in .txt
                """.format(localfile)
                send_mail(None, TO, SUBJECT, FROM, TEMPLATE, body)
                logger.error(body)
    else:
        # Email there was no file found on the Common App server
        body = "The directory is empty no source file was found."
        send_mail(None, TO, SUBJECT, FROM, TEMPLATE, body)
        logger.error(body)
    # set destination directory for which the sql file will be archived to
    archived_destination = ('{0}commonapp_output-{1}.sql'.format(
        settings.COMMONAPP_CSV_ARCHIVED, datetimestr,
    ))
    # Check to see if sql file exists, if not send Email
    if os.path.isfile(sqloutput):
        # rename and move the file to the archive directory
        shutil.move(sqloutput, archived_destination)
    else:
        # email there was no file found on the Common App server
        body = "There was no .sql output file to move."
        send_mail(None, TO, SUBJECT, FROM, TEMPLATE, body)
        logger.error(body)


if __name__ == "__main__":
    args = parser.parse_args()
    test = args.test
    database = args.database

    if database:
        database = database.lower()
    else:
        print("mandatory option missing: database name\n")
        parser.print_help()
        sys.exit()

    if database not in {'cars', 'train'}:
        print("database must be: 'cars' or 'train'\n")
        parser.print_help()
        sys.exit()

    if database == 'cars':
        earl = settings.INFORMIX_ODBC
    elif database == 'train':
        earl = settings.INFORMIX_ODBC_TRAIN
    else:
        print('invalid database name: {0}'.format(database))
        sys.exit()

    sys.exit(main())
