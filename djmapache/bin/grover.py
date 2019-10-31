# -*- coding: utf-8 -*-

import os, sys
import csv
import argparse
import logging

# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.shell')

# required if using django models
import django
django.setup()

from django.conf import settings
from djmapache.sql.grover import ALUMNI, FACSTAFF, STUDENT
from djimix.core.utils import get_connection, xsql

logger = logging.getLogger('djmapache')

# set up command-line options
desc = """
    Accepts as input a group type: student, faculty, staff, or alumni
"""

parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument(
    '-w', '--who',
    required=True,
    help="student, faculty, staff, or alumni",
    dest='who'
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test'
)


def main():

    headers = {}
    headers['faculty'] = [
        'User Type','Email Address','Database Key','First Name','Last Name',
        'Preferred Name','Previous Last Name'
    ]
    headers['staff'] = headers['faculty']
    headers['student'] = headers['staff'] + [
        'Transcript First Name','Transcript Last Name',
        'Concentration','Majors Admin Only','Minors Admin Only'
    ]
    headers['alumni'] = headers['student'] + [
        'Social Class Year','Graduation Year Admin Only'
    ]

    if who == 'faculty' or who == 'staff':
        where = 'provisioning_vw.{} IS NOT NULL'.format(who)
        sql = FACSTAFF(where)
    elif who == 'student':
        sql = STUDENT
    elif who == 'alumni':
        sql = ALUMNI
    else:
        print("who must be: 'student', 'faculty', 'staff', or 'alumni'\n")
        exit(-1)

    if test:
        print("who = {}".format(who))
        print(headers[who])
        print("sql = {}".format(sql))
        logger.debug("sql = {}".format(sql))
        exit(-1)

    connection = get_connection()
    with connection:
        rows = xsql(sql, connection).fetchall()

    phile = r'{}.csv'.format(who)
    with open(phile, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([x for x in headers[who]])
        for row in rows:
            writer.writerow(row)

    print('done. created file: {}'.format(phile))


if __name__ == '__main__':
    args = parser.parse_args()
    who = args.who
    test = args.test

    if test:
        print(args)

    sys.exit(main())
