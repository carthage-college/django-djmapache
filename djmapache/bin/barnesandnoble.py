#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import django
import os
import pysftp
import shutil
import sys
import time

from django.conf import settings
from djimix.core.utils import get_connection
from djimix.core.utils import xsql
from djtools.utils.mail import send_mail


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
    # Host sftp.bncollege.com
    #   HostName sftp.bncollege.com
    #   HostKeyAlgorithms=+ssh-dss
    ###########################################################################

    datetimestr = time.strftime('%Y%m%d%H%M%S')
    sqldict = {
        'AR100': 'stu_acad_rec_100',
        'AR200': 'stu_acad_rec_200',
        'EXENRCRS': 'exenrcrs',
    }
    ###########################################################################
    # Dict Value stu_acad_rec_100 selects active students and sets budget
    # limit for export (books = '100' & $3000.00)
    #
    # Dict Value stu_acad_rec_200 selects active students and sets budget
    # limit for export (supplies = '200' & $50.00)
    #
    # Dict Value 'EXENCRS' selects all current and future course-sections
    # (sec_rec) and instructor for Bookstore to order ISBN inventory
    ###########################################################################

    for name, incantation in sqldict.items():
        phile = os.path.join(
            BASE_DIR, 'sql/barnesandnoble/{0}.sql'.format(incantation),
        )
        with open(phile) as sql_file:
            sqldict[name] = sql_file.read()

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # sFTP connection information for Barnes and Noble 1
    xtrnl_connection1 = {
        'host': settings.BARNESNOBLE1_HOST,
        'username': settings.BARNESNOBLE1_USER,
        'password': settings.BARNESNOBLE1_PASS,
        'port': settings.BARNESNOBLE1_PORT,
        'cnopts': cnopts,
    }
    # sFTP connection information for Barnes and Noble 2
    xtrnl_connection2 = {
        'host': settings.BARNESNOBLE2_HOST,
        'username': settings.BARNESNOBLE2_USER,
        'password': settings.BARNESNOBLE2_PASS,
        'port': settings.BARNESNOBLE2_PORT,
        'cnopts': cnopts,
    }

    for key, sql in sqldict.items():
        if DEBUG:
            print(key)
            # print(sql)
        with get_connection() as connection:
            rows = xsql(sql, connection, key=INFORMIX_DEBUG).fetchall()
            if rows:
                # set directory and filename to be stored
                filename = (
                    '{0}{1}.csv'.format(settings.BARNESNOBLE_CSV_OUTPUT, key)
                )
                # set destination path and new filename to which it
                # will be renamed when archived
                archive_destination = ('{0}{1}_{2}_{3}.csv'.format(
                    settings.BARNESNOBLE_CSV_ARCHIVED,
                    'CCBAK',
                    key,
                    datetimestr,
                ))
                # create .csv file
                with open(filename, 'w') as csvfile:
                    output = csv.writer(csvfile)
                    # write header row to file
                    if DEBUG:
                        # write header row for (AR100, AR200)
                        if key in {'AR100', 'AR200'}:
                            output.writerow([
                                'StudentID',
                                'Elastname',
                                'Efirstname',
                                'Xmiddleinit',
                                'Xcred_limit',
                                'EProviderCode',
                                'Ebegdate',
                                'Eenddate',
                                'Eidtype',
                                'Erecordtype',
                                'Eaccttype',
                            ])
                        else:  # write header row for EXENCRS
                            output.writerow([
                                'bnUnitNo',
                                'bnTerm',
                                'bnYear',
                                'bnDept',
                                'bnCourseNo',
                                'bnSectionNo',
                                'bnProfName',
                                'bnMaxCapcty',
                                'bnEstEnrlmnt',
                                'bnActEnrlmnt',
                                'bnContdClss',
                                'bnEvngClss',
                                'bnExtnsnClss',
                                'bnTxtnetClss',
                                'bnLoctn',
                                'bnCourseTitl',
                                'bnCourseID',
                            ])
                    for row in rows:
                        output.writerow(row)
            else:  # no rows
                print('No values in list')

        # renaming old filename to newfilename and move to archive location
        shutil.copy(filename, archive_destination)

    # end loop on rows
    # set local path {/data2/www/data/barnesandnoble/}
    source_dir = ('{0}'.format(settings.BARNESNOBLE_CSV_OUTPUT))
    # set local path and filenames
    # variable == /data2/www/data/barnesandnoble/{filename.csv}
    file_ar100 = '{0}AR100.csv'.format(source_dir)
    file_ar200 = '{0}AR200.csv'.format(source_dir)
    file_exencrs = '{0}EXENRCRS.csv'.format(source_dir)
    # for final email status
    success = True
    # sFTP PUT moves the EXENCRS.csv file to the Barnes & Noble server 1
    try:
        with pysftp.Connection(**xtrnl_connection1) as sftp:
            if DEBUG:
                print(file_exencrs)
            sftp.put(file_exencrs, preserve_mtime=True)
            # deletes original file from our server
            os.remove(file_exencrs)
    except Exception as error:
        success = False
        body = """
            Unable to PUT EXENCRS.csv to Barnes and Noble server.\n\n{0}
        """.format(error)
        send_mail(
            None,
            TO,
            SUBJECT(status='failed'),
            FROM,
            'email.html',
            body,
        )
        if DEBUG:
            print(error)
    # sFTP PUT moves the AR100.csv file to the Barnes & Noble server 2
    try:
        with pysftp.Connection(**xtrnl_connection2) as sftp_ar100:
            if DEBUG:
                sftp_ar100.chdir('TestFiles/')
                print(file_ar100)
            sftp_ar100.put(file_ar100, preserve_mtime=True)
            sftp_ar100.chdir('ToBNCB/')
            sftp_ar100.put(file_ar100, preserve_mtime=True)
            # deletes original file from our server
            os.remove(file_ar100)
    except Exception as error_ar100:
        success = False
        body = """
            Unable to PUT AR100.csv to Barnes and Noble server.\n\n{0}
        """.format(error_ar100)
        send_mail(
            None,
            TO,
            SUBJECT(status='failed'),
            FROM,
            'email.html',
            body,
        )
        if DEBUG:
            print(error_ar100)
    # sFTP PUT moves the AR200.csv file to the Barnes & Noble server 2
    try:
        with pysftp.Connection(**xtrnl_connection2) as sftp_ar200:
            sftp_ar200.put(file_ar200, preserve_mtime=True)
            sftp_ar200.chdir('ToBNCB/')
            sftp_ar200.put(file_ar200, preserve_mtime=True)
            # deletes original file from our server
            os.remove(file_ar200)
    except Exception as error_ar200:
        success = False
        body = """
            Unable to PUT AR200.csv to Barnes and Noble server.\n\n{0}
        """.format(error_ar200)
        send_mail(
            None,
            TO,
            SUBJECT(status='failed'),
            FROM,
            'email.html',
            body,
        )
        if DEBUG:
            print(error_ar200)

    # sFTP upload complete send success message
    if success:
        body = 'The Barnes and Noble files were successfully uploaded.'
        subject = SUBJECT(status='success')
        send_mail(None, TO, subject, FROM, 'email.html', body)


if __name__ == '__main__':

    sys.exit(main())
