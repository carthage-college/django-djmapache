#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import django
import os
import pysftp
import sys
import time

from django.conf import settings
from djimix.core.utils import get_connection
from djimix.core.utils import xsql
from djtools.utils.mail import send_mail


# django settings for shell environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.local')
# prime django
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
desc = "Everbridge Upload."

parser = argparse.ArgumentParser(description=desc)
parser.add_argument(
    '-t',
    '--test',
    action='store_true',
    help='Dry run?',
    dest='test',
)
parser.add_argument(
    '-l',
    '--limit',
    help='Limit results to n',
    required=False,
    dest='limit',
)
parser.add_argument(
    '-d',
    '--database',
    help='database name.',
    dest='database',
)

TO = settings.EVERBRIDGE_TO_EMAIL
FROM = settings.EVERBRIDGE_FROM_EMAIL


def main():
    """Send all student, adult, facstaff records to everbridge."""
    # determines which database is being called from the command line
    if database == 'cars':
        earl = settings.INFORMIX_ODBC
    elif database == 'sandbox':
        earl = settings.INFORMIX_ODBC_SANDBOX
    elif database == 'train':
        earl = settings.INFORMIX_ODBC_TRAIN
    else:
        print('invalid database name: {0}'.format(database))
        sys.exit()

    for key in ('students', 'adult', 'facstaff'):
        sql_file = os.path.join(
            settings.BASE_DIR, 'sql/everbridge/{0}.sql'.format(key),
        )
        with open(sql_file) as incantation:
            sql = incantation.read()

        if limit:
            sql += 'LIMIT {0}'.format(limit)
        if test:
            print('key = {0}, sql = {1}'.format(key, sql))

        badmatches = []
        with get_connection(earl) as connection:
            rows = xsql(sql, connection, key=settings.INFORMIX_DEBUG).fetchall()
            if rows:
                if test:
                    print("rows {0}".format(len(rows)))
                filename = ('{0}{1}_upload_{2}.csv'.format(
                    settings.EVERBRIDGE_CSV_OUTPUT,
                    key,
                    time.strftime('%Y%m%d%H%M%S'),
                ))
                with open(filename, 'w') as csv_file:
                    output = csv.writer(
                        csv_file, dialect='excel', lineterminator='\n',
                    )
                    if key == 'facstaff':  # write header row for FacStaff
                        output.writerow(settings.EVERBRIDGE_FACSTAFF_HEADERS)
                    else:  # write header row for Student and Adult
                        output.writerow(settings.EVERBRIDGE_STUDENT_HEADERS)
                    for row in rows:
                        if row.customvalue1:
                            row.customvalue1 = row.customvalue1.strip()
                        output.writerow(row)
                        if test:
                            print("row = \n{0}".format(row))
                        # checking for Bad match in either students or facstaff
                        if row and ((row.customvalue1 and 'Bad match:' in row.customvalue1) \
                        or (row.customvalue2 and 'Bad match:' in row.customvalue2)):
                            badmatches.append("""
                                {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8},
                                {9}, {10} {11} {12}, {13}, {14}, {15}, {16},
                                {17}, {18}, {19} {20}\n\n
                            """.format(
                                row.lastname,
                                row.firstname,
                                row.middleinitial,
                                row.suffix,
                                row.externalid,
                                row.country,
                                row.businessname,
                                row.recordtype,
                                row.phone1,
                                row.phonecountry1,
                                row.emailaddress1,
                                row.emailaddress2,
                                row.sms1,
                                row.sms1country,
                                row.customfield1,
                                row.customvalue1,
                                row.customfield2,
                                row.customvalue2,
                                row.customfield3,
                                row.customvalue3,
                                row.end,
                            ))
                        badmatches_table = ''.join(badmatches)
                        if test:
                            print("badmatches = \n{0}".format(badmatches))
                    if badmatches:
                        if test:
                            print("badmatches_table = \n{0}".format(
                                badmatches_table,
                            ))
                            print("length of badmatches = {0}.".format(
                                len(badmatches),
                            ))
                        body = """
                            A bad match exists in the file we are sending to
                            Everbridge.\n\n{0}\n\n
                            Bad match records: {1}
                        """.format(badmatches_table, len(badmatches))
                        send_mail(
                            None,
                            TO,
                            '[Everbridge] Bad match',
                            FROM,
                            'email.html',
                            body,
                        )
                    else:
                        print('No bad matches found.')

                if not test:
                    # SFTP the CSV
                    try:
                        print('sftp attempt')
                        print(filename)
                        # go to our storage directory on the server
                        os.chdir(settings.EVERBRIDGE_CSV_OUTPUT)
                        cnopts = pysftp.CnOpts()
                        cnopts.hostkeys = None
                        xtrnl_connection = {
                            'host': settings.EVERBRIDGE_HOST,
                            'username': settings.EVERBRIDGE_USER,
                            'private_key': settings.EVERBRIDGE_PKEY,
                            'cnopts': cnopts,
                        }
                        with pysftp.Connection(**xtrnl_connection) as sftp:
                            sftp.chdir("replace/")
                            print("current working directory: {0}".format(
                                sftp.getcwd(),
                            ))
                            #sftp.put(filename, preserve_mtime=True)
                            print("file uploaded:")
                            for phile in sftp.listdir():
                                print(phile)
                                print(str(sftp.lstat(phile)))
                            sftp.close()
                        print("sftp put success: {0}".format(key))
                    except Exception as error:
                        print('sftp put fail [{0}]: {1}'.format(key, error))
                        body = """
                            Unable to PUT upload to Everbridge server.\n\n{0}
                        """.format(error)
                        send_mail(
                            None,
                            TO,
                            '[Everbridge SFTP] {0} failed'.format(key),
                            FROM,
                            'email.html',
                            body,
                        )
                else:
                    print("TEST: no sftp")
            else:
                print("No results from the database for {0}".format(key))

    print("Done")


if __name__ == "__main__":

    args = parser.parse_args()
    test = args.test
    limit = args.limit
    database = args.database

    if database:
        database = database.lower()
    else:
        print("mandatory option missing: database name")
        parser.print_help()
        sys.exit()

    if database not in {'cars', 'train', 'sandbox'}:
        print("database must be: 'cars' or 'train' or 'sandbox'\n")
        parser.print_help()
        sys.exit()

    sys.exit(main())
