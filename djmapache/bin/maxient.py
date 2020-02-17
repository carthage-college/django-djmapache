#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import pysftp
import sys

from django.conf import settings
from djimix.core.utils import get_connection
from djimix.core.utils import xsql
from djtools.utils.mail import send_mail


# django settings for shell environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.local')
# prime django
import django
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


def main():
    """Maxient Upload via sftp."""
    phile = os.path.join(
        settings.BASE_DIR, 'sql/maxient/demographic.sql',
    )
    with open(phile) as incantation:
        sql = incantation.read()

    with get_connection() as connection:
        rows = xsql(sql, connection, key=settings.INFORMIX_DEBUG).fetchall()

        if rows:
            # set directory and filename
            filename = ('{0}CARTHAGE_DEMOGRAPHICS_DATA.txt'.format(
                settings.MAXIENT_CSV_OUTPUT,
            ))
            # create txt file using pipe delimiter
            with open(filename, 'w') as maxientfile:
                output = csv.writer(maxientfile, delimiter='|')
                if DEBUG:
                    # No Header required but used for testing
                    output.writerow(settings.MAXIENT_HEADERS)
                for row in rows:
                    output.writerow(row)

            # SFTP connection information
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            xtrnl_connection = {
                'host': settings.MAXIENT_HOST,
                'username': settings.MAXIENT_USER,
                'private_key': settings.MAXIENT_PKEY,
                'private_key_pass': settings.MAXIENT_PASS,
                'cnopts': cnopts,
            }
            # go to our storage directory on the server
            os.chdir(settings.MAXIENT_CSV_OUTPUT)
            try:
                with pysftp.Connection(**xtrnl_connection) as sftp:
                    sftp.chdir('incoming/')
                    sftp.put(filename, preserve_mtime=True)
                if DEBUG:
                    print("success: MAXIENT UPLOAD")
            except Exception as error:
                send_mail(
                    None,
                    settings.MAXIENT_TO_EMAIL,
                    '[Maxient SFTP] MAXIENT UPLOAD failed',
                    settings.MAXIENT_FROM_EMAIL,
                    'email.html',
                    'Unable to upload to Maxient server.\n\n{0}'.format(error),
                )
                if DEBUG:
                    print(error)
        else:
            print('There was a no values in list error')


if __name__ == "__main__":

    sys.exit(main())
