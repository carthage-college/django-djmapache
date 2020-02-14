#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
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
# need for templates
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


TO = settings.CONCIERGE_TO_EMAIL
FROM = settings.CONCIERGE_FROM_EMAIL
DEBUG = settings.DEBUG
SUBJECT = 'Concierge Upload: {status}'.format

desc = """
    Package Concierge is an automated, self-service locker system that allows
    students to retrieve their packages when it is convenient for them.
"""
parser = argparse.ArgumentParser(description=desc)
parser.add_argument(
    '-d',
    '--database',
    help='database name.',
    dest='database',
)


def file_upload(phile):
    """Transfers the students.csv file to the Package Concierge server."""
    # by adding cnopts, I'm authorizing the program to ignore the host key
    # and just continue
    cnopts = pysftp.CnOpts()
    # ignore known host key checking
    cnopts.hostkeys = None
    # sFTP connection information for Package Concierge
    xtrnl_connection = {
        'host': settings.CONCIERGE_HOST,
        'username': settings.CONCIERGE_USER,
        'password': settings.CONCIERGE_PASS,
        'port': settings.CONCIERGE_PORT,
        'cnopts': cnopts,
    }
    try:
        with pysftp.Connection(**xtrnl_connection) as sftp:
            # sftp files if they end in .csv
            sftp.put(phile, preserve_mtime=True)
        # delete original files from our server
        os.remove(phile)
    except Exception as error:
        body = """
            Unable to PUT .csv files to Package Concierge server.\n\n{0}
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


def main():
    """Barnes and Noble Upload."""
    # determines which database is being called from the command line
    if database == 'cars':
        earl = settings.INFORMIX_ODBC
    elif database == 'train':
        earl = settings.INFORMIX_ODBC_TRAIN
    else:
        print('invalid database name: {0}'.format(database))
        sys.exit()
    # formatting date and time string
    datetimestr = time.strftime('%Y%m%d%H%M%S')
    phile = os.path.join(
        settings.BASE_DIR, 'sql/concierge/students.sql',
    )
    with open(phile) as incantation:
        sql = incantation.read()

    with get_connection(earl) as connection:
        rows = xsql(sql, connection, key=settings.INFORMIX_DEBUG).fetchall()
        if rows:
            # set directory and filename to be stored
            filename = '{0}students.csv'.format(settings.CONCIERGE_CSV_OUTPUT)
            # set destination path and new filename that it will be renamed to
            # when archived
            archive_destination = ('{0}students_bak_{1}.csv'.format(
                settings.CONCIERGE_CSV_ARCHIVED,
                datetimestr,
            ))
            # create .csv file
            with open(filename, 'w') as csvfile:
                output = csv.writer(csvfile)
                output.writerow([
                    'Unit Code',
                    'First Name',
                    'Last Name',
                    'Email Address',
                    'Cell Phone',
                ])
                # creating the data rows for the .csv files
                for row in rows:
                    output.writerow([
                        row.unitcode,
                        row.firstname,
                        row.lastname,
                        row.emailaddress,
                        row.cellphone,
                    ])

            # renaming old filename to newfilename and move to archive location
            shutil.copy(filename, archive_destination)
        else:
            send_mail(
                None,
                TO,
                SUBJECT(status='failed'),
                FROM,
                'email.html',
                'No values in list.',
            )

    if not DEBUG:
        file_upload(filename)


if __name__ == '__main__':
    args = parser.parse_args()
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

    sys.exit(main())
