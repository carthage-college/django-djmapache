import os
import sys
import pysftp
import csv
import argparse

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


def main():
    """Maxient Upload via sftp."""
    # go to our storage directory on the server
    os.chdir(settings.MAXIENT_CSV_OUTPUT)
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # SFTP connection information
    XTRNL_CONNECTION = {
       'host':settings.MAXIENT_HOST,
       'username':settings.MAXIENT_USER,
       'private_key':settings.MAXIENT_PKEY,
       'private_key_pass':settings.MAXIENT_PASS,
       'cnopts':cnopts
    }
    # Run SQL statement
    sqlresult = do_sql(DEMOGRAPHIC_DATA, earl=EARL)
    # set directory and filename
    filename=('{0}CARTHAGE_DEMOGRAPHICS_DATA.txt'.format(
        settings.MAXIENT_CSV_OUTPUT
    ))
    # create txt file using pipe delimiter
    maxientfile = open(filename,'w');
    output=csv.writer(maxientfile, delimiter='|')

    if DEBUG:
        # No Header required but used for testing
        output.writerow(HEADERS)

    # create file
    if sqlresult is not None:
        for row in sqlresult:
            output.writerow(row)
    else:
        print('There was a no values in list error')
    maxientfile.close()

    try:
        with pysftp.Connection(**XTRNL_CONNECTION) as sftp:
            sftp.chdir("incoming/")
            sftp.put(filename, preserve_mtime=True)
            sftp.close()
        if DEBUG:
            print("success: MAXIENT UPLOAD")
    except Exception as error:
        SUBJECT = '[Maxient SFTP] MAXIENT UPLOAD failed'
        BODY = 'Unable to PUT upload to Maxient server.\n\n{0}'.format(error)
        sendmail(
            settings.MAXIENT_TO_EMAIL,settings.MAXIENT_FROM_EMAIL,
            SUBJECT, BODY
        )
        if DEBUG:
            print(error)

if __name__ == "__main__":
    args = parser.parse_args()

    sys.exit(main())
