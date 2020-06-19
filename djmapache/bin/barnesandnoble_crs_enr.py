#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import django
import os
import pysftp
import sys
import shutil
import zipfile
import os.path
from os import path

from django.conf import settings
from djimix.core.utils import get_connection
from djimix.core.utils import xsql
from djtools.utils.mail import send_mail

from djmapache.sql.barnesandnoble.crs_enr_sql import COURSES, USERS, \
    ENROLLMENTS

# django settings for shell environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.shell')

# required for interacting with django infrastructure e.g. templates
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

DEBUG = settings.DEBUG
INFORMIX_DEBUG = settings.INFORMIX_DEBUG
BASE_DIR = settings.BASE_DIR
TO = settings.BARNESNOBLE_TO_EMAIL
FROM = settings.BARNESNOBLE_FROM_EMAIL
SUBJECT = "[Barnes & Noble] upload {status}".format


def fn_format_date(date):
    if len(date) == 10:
        ret = date[6:] + "-" + date[:2] + '-' + date[3:5]
    else:
        ret = ""
    return ret

def main():
    """Barnes and Noble Upload."""
    ###########################################################################
    # OpenSSH 7.0 and greater disable the ssh-dss (DSA) public key algorithm,
    # which B&N use for authentication on their servers, so you have to add
    # ssh-dss to the ssh/sftp command:
    #
    # -oHostKeyAlgorithms=+ssh-dss
    #
    # or add the following to the cron user's .ssh/config file:
    #
    # Host rex-sftp.bncollege.com
    #   HostName rex-sftp.bncollege.com
    #   HostKeyAlgorithms=+ssh-dss
    ###########################################################################

    # Defines file names and directory location
    # bn_course_fil = ('{0}carthage_students.txt'.format(
    #     settings.ADIRONDACK_TXT_OUTPUT)
    # )

    # bn_course_file = settings.BARNES_N_NOBLE_CSV_OUTPUT + "courses.csv"
    # bn_enr_fil = settings.BARNES_N_NOBLE_CSV_OUTPUT + "enrollments.csv"
    # bn_usr_fil = settings.BARNES_N_NOBLE_CSV_OUTPUT + "users.csv"
    # bn_zip_fil = settings.BARNES_N_NOBLE_CSV_OUTPUT + "carthage_bn"

    bn_course_file = "courses.csv"
    bn_enr_fil = "enrollments.csv"
    bn_usr_fil = "users.csv"
    bn_zip_fil = "carthage_bn.zip"

    # print(settings.BARNES_N_NOBLE_CSV_OUTPUT + bn_zip_fil)
    if path.exists(settings.BARNES_N_NOBLE_CSV_OUTPUT + bn_zip_fil):
        os.remove(settings.BARNES_N_NOBLE_CSV_OUTPUT + bn_zip_fil)

    """Create the headers for the three files"""
    fil = open(bn_course_file, 'w')
    fil.write("recordNumber,campus,school,institutionDepartment,term,"
              "department,course,section,campusTitle,schoolTitle,"
              "institutionDepartmentTitle,courseTitle,"
              "institutionCourseCode,institutionClassCode,"
              "institutionSubjectCodes,institutionSubjectsTitle,"
              "crn,termTitle,termType,termStartDate,termEndDate,"
              "sectionStartDate,sectionEndDate,classGroupId,"
              "estimatedEnrollment" + "\n")
    fil.close()

    fil1 = open(bn_enr_fil, 'w')
    fil1.write("recordNumber,campus,school,institutionDepartment,term,"
               "department,course,section,email,firstName,middleName,"
               "lastName,userRole,sisUserId,includedInCourseFee,"
               "studentFullPartTimeStatus,creditHours" + "\n")
    fil1.close()


    fil2 = open(bn_usr_fil, 'w')
    fil2.write("recordNumber,campus,school,email,firstName,middleName,"
               "lastName,userRole,sisUserId" + "\n")
    fil2.close()


    try:
        # set global variable
        # global EARL
        # # determines which database is being called from the command line
        # if database == 'cars':
        EARL = settings.INFORMIX_ODBC
        # elif database == 'train':
        #     EARL = settings.INFORMIX_ODBC_TRAIN
        # else:
        #     print("database must be: 'cars' or 'train'")
        #     exit(-1)
        # # --------------------------
        # Create the txt file
        # print(EARL)

        crs_qry = COURSES

        connection = get_connection(EARL)
        # connection closes when exiting the 'with' block
        with connection:
            data_result = xsql(
                crs_qry, connection, key=settings.INFORMIX_DEBUG
            ).fetchall()

            ret = list(data_result)
            if ret is None:
                print("No result")
                # SUBJECT = "[Adirondack] Application failed"
                # BODY = "SQL Query returned no data."
                # send_mail(
                #     None, [settings.ADIRONDACK_TO_EMAIL, ], SUBJECT,
                #     settings.ADIRONDACK_FROM_EMAIL, 'email/default.html',
                #     BODY, [settings.ADMINS[0][1], ]
                # )
            else:
                # print(ret)
                cnt = 1
                print("Open file 1")
                fil = open(bn_course_file, 'a')
                for row in ret:
                    # fil.write(row)
                    campus = '"' + row[0] + '"'
                    school = '"' + row[1] + '"'
                    institutionDepartment = row[2]
                    term = '"' + row[3] + '"'
                    department = '"' + row[4] + '"'
                    course = '"' + row[5] + '"'
                    SectionCode  = '"' + row[6] + '"'
                    campusTitle = '"' + row[7] + '"'
                    schoolTitle  = '"' + row[8] + '"'
                    institutionDepartmentTitle = '"' + row[9] + '"'
                    courseTitle = '"' + row[10] + '"'
                    institutionCourseCode = '"' + row[11] + '"'
                    institutionClassCode = '"' + row[12] + '"'
                    institutionSubjectCodes = '"' + row[13] + '"'
                    institutionSubjectsTitle = '"' + row[14] + '"'
                    crn = '"' + row[15] + '"'
                    termTitle = '"' + row[16] + '"'
                    termType = '"' + row[17] + '"'
                    termStartDate = '"' + fn_format_date(row[18]) + '"'
                    termEndDate = '"' + fn_format_date(row[19]) + '"'
                    sectionStartDate = '"' + fn_format_date(row[20]) + '"'
                    sectionEndDate = '"' + fn_format_date(row[21]) + '"'
                    classGroupId  = '"' + row[22] + '"'
                    estimatedEnrollment  =  str(row[23])

                    lin = str(cnt) + "," + campus + "," + school + "," + \
                        institutionDepartment + "," + term + "," + \
                        department + "," + course + "," + SectionCode + "," + \
                        campusTitle + "," + schoolTitle + "," + \
                        institutionDepartmentTitle + "," + courseTitle \
                        + "," + institutionCourseCode + "," + \
                        institutionClassCode + "," + institutionSubjectCodes \
                        + "," + institutionSubjectsTitle + "," + crn + "," + \
                        termTitle + "," + termType + "," + termStartDate \
                        + "," + termEndDate + "," + sectionStartDate + "," + \
                        sectionEndDate + "," + classGroupId + "," + \
                        estimatedEnrollment + "\n"

                    fil.write(lin)
                    cnt = cnt + 1
                fil.close()
                print("Close file 1")


        connection = get_connection(EARL)
        # connection closes when exiting the 'with' block
        with connection:
            data_result = xsql(
                USERS, connection, key=settings.INFORMIX_DEBUG
            ).fetchall()

            ret = list(data_result)
            if ret is None:
                print("No result")
                # SUBJECT = "[Adirondack] Application failed"
                # BODY = "SQL Query returned no data."
                # send_mail(
                #     None, [settings.ADIRONDACK_TO_EMAIL, ], SUBJECT,
                #     settings.ADIRONDACK_FROM_EMAIL, 'email/default.html',
                #     BODY, [settings.ADMINS[0][1], ]
                # )
            else:
                # print(ret)
                cnt = 1
                print("Open file 2")

                fil2 = open(bn_usr_fil, 'a')
                for row in ret:
                    # print(row)
                    campus = '"' + row[0] + '"'
                    school = '"' + row[1] + '"'
                    email = '"' + row[2] + '"'
                    firstname = '"' + row[3] + '"'
                    middlename = '"' + row[4] + '"'
                    lastname = '"' + row[5] + '"'
                    role = '"' + row[6].strip() + '"'
                    username = '"' + row[7] + '"'

                    lin = str(cnt) + "," + campus + "," + school + "," + \
                          email + "," + firstname + "," + \
                          middlename + "," + lastname + "," + role + "," + \
                          username + "\n"

                    # print(lin)

                    fil2.write(lin)
                    cnt = cnt + 1
                fil2.close()
                print("Close file 2")



        connection = get_connection(EARL)
        # connection closes when exiting the 'with' block
        with connection:
            data_result = xsql(
                ENROLLMENTS, connection, key=settings.INFORMIX_DEBUG
            ).fetchall()

            ret = list(data_result)
            if ret is None:
                print("No result")
                # SUBJECT = "[Adirondack] Application failed"
                # BODY = "SQL Query returned no data."
                # send_mail(
                #     None, [settings.ADIRONDACK_TO_EMAIL, ], SUBJECT,
                #     settings.ADIRONDACK_FROM_EMAIL, 'email/default.html',
                #     BODY, [settings.ADMINS[0][1], ]
                # )
            else:
                # print(ret)
                cnt = 1
                print("Open file 3")
                fil3 = open(bn_enr_fil, 'a')
                for row in ret:
                    # print(row)
                    campus = '"' + row[0] + '"'
                    school = '"' + row[1] + '"'
                    inst_dept = '"' + row[2] + '"'
                    term = '"' + row[3] + '"'
                    dept = '"' + row[4] + '"'
                    course = '"' + row[5] + '"'
                    section = '"' + row[6].strip() + '"'
                    email = '"' + row[7] + '"'

                    firstname = '"' + row[8] + '"'
                    middlename = '"' + row[9] + '"'
                    lastname = '"' + row[10] + '"'
                    role = '"' + row[11] + '"'
                    userid = '"' + str(row[12]) + '"'
                    includeinfee = '"' + row[13] + '"'
                    fulltimestatus = '"' + row[14] + '"'
                    credit_hours = '"' + str(row[15]) + '"'

                    lin = str(cnt) + "," + campus + "," + school + "," + \
                          inst_dept + "," + term + "," + \
                          dept + "," + course + "," + \
                          section + "," + email + "," + \
                          firstname + "," + middlename + "," + \
                          lastname + "," + role + "," + userid + "," + \
                          includeinfee + "," + fulltimestatus + "," + \
                          credit_hours +  "\n"

                    # print(lin)
                    fil3.write(lin)
                    cnt = cnt + 1
                fil3.close()
                print("Close file 1")

        print(bn_zip_fil)
        print('creating archive')
        zf = zipfile.ZipFile(bn_zip_fil, mode='w')

        print('add files')

        zf.write(bn_course_file)
        zf.write(bn_usr_fil)
        zf.write(bn_enr_fil)

        print("Move zip file")
        shutil.move(bn_zip_fil,settings.BARNES_N_NOBLE_CSV_OUTPUT)

        print("Remove temp csv files")
        os.remove(bn_usr_fil)
        os.remove(bn_course_file)
        os.remove(bn_enr_fil)

    # cnopts = pysftp.CnOpts()
    # cnopts.hostkeys = None
    # # sFTP connection information for Barnes and Noble 1
    # xtrnl_connection1 = {
    #     'host': settings.BARNESNOBLE1_HOST,
    #     'username': settings.BARNESNOBLE1_USER,
    #     'password': settings.BARNESNOBLE1_PASS,
    #     'port': settings.BARNESNOBLE1_PORT,
    #     'cnopts': cnopts,
    # }
    # try:
    #     with pysftp.Connection(**xtrnl_connection1) as sftp:
    #         if DEBUG:
    #             print(file_exencrs)
    #         sftp.put(file_exencrs, preserve_mtime=True)
    #         # deletes original file from our server
    #         os.remove(file_exencrs)
    # except Exception as error:
    #     success = False
    #     body = """
    #            Unable to PUT EXENCRS.csv to Barnes and Noble server.\n\n{0}
    #        """.format(error)
    #     send_mail(
    #         None,
    #         TO,
    #         SUBJECT(status='failed'),
    #         FROM,
    #         'email.html',
    #         body,
    #     )
    #     if DEBUG:
    #         print(error)

    except Exception as e:
        print("Error in main:  " + str(e))
        # fn_write_error("Error in barnesandnoble_crs_enr.py - Main: "
        #                + repr(e))
        # fn_send_mail(settings.BB_SKY_TO_EMAIL,
        #              settings.BB_SKY_FROM_EMAIL, "SKY API ERROR", "Error in "
        #                         "barnesandnoble_crs_enr.py - for: " + + repr(e))


if __name__ == "__main__":
    sys.exit(main())
