#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import django
import os
import pysftp
import sys

from django.conf import settings
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
SUBJECT = "[Barnes & Noble] AIP upload {status}".format


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

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    xtrnl_connection = {
        'host': settings.BARNESNOBLE_AIP_HOST,
        'username': settings.BARNESNOBLE_AIP_USER,
        'port': settings.BARNESNOBLE_AIP_PORT,
        'private_key': settings.BARNESNOBLE_AIP_KEY,
        'cnopts': cnopts,
    }

    phile = os.path.join(settings.BARNESNOBLE_AIP_DATA, 'test.csv')

    try:
        with pysftp.Connection(**xtrnl_connection) as sftp:
            sftp.cwd('inbox')
            if DEBUG:
                print('put phile')
                print(phile)
            sftp.put(phile)
            if DEBUG:
                for attr in sftp.listdir_attr():
                    print(attr.filename, attr)
            sftp.close()
        success = True
    except Exception as error:
        success = False
        body = """
            Unable to PUT AIP file to Barnes and Noble server.\n\n{0}
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

    # sFTP upload complete send success message
    if success:
        body = '[Barnes and Noble] AIP files were successfully uploaded.'
        subject = SUBJECT(status='success')
        send_mail(None, TO, subject, FROM, 'email.html', body)


if __name__ == '__main__':

    sys.exit(main())
