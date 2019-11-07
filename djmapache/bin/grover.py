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
from djimix.core.utils import get_connection, xsql

logger = logging.getLogger('djmapache')

# set up command-line options
desc = """
    Accepts as input a group type: student, facstaff, alumni, or educatdion
"""

parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument(
    '-w', '--who',
    required=True,
    help="student, facstaff, alumni, or education",
    dest='who'
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test'
)

HEADERS = {}
HEADERS['facstaff'] = [
    'User Type','Email Address','Database Key','Last Name','First Name',
    'Preferred Name','Previous Last Name'
]
HEADERS['alumni'] = HEADERS['student'] = HEADERS['facstaff'] + [
    'Transcript First Name','Transcript Last Name',
    'Concentration','Majors Admin Only','Minors Admin Only',
    'Social Class Year','Graduation Year Admin Only'
]
HEADERS['education'] = [
    'User Type','Email Address','Database Key','Graduation Year','School',
    'Degree Type','Majors','Minors'
]


def main():

    # check for profile type will fail if not one of the four allowed types
    try:
        headers = HEADERS[who]
    except:
        print("who must be: 'student', 'facstaff', 'alumni', or 'education'\n")
        exit(-1)

    phile = '{}/sql/grover/{}.sql'.format(settings.BASE_DIR,who)
    with open(phile) as incantation:
        sql = incantation.read()

    if test:
        print("who = {}".format(who))
        print(headers)
        print("sql = {}".format(sql))
        logger.debug("sql = {}".format(sql))
        phile = '{}/sql/grover/{}.sql'.format(settings.BASE_DIR,who)
        exit(-1)

    connection = get_connection()
    with connection:
        rows = xsql(sql, connection, key=settings.INFORMIX_DEBUG).fetchall()

    phile = r'{}.csv'.format(who)
    with open(phile, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='|')
        writer.writerow([x for x in headers])
        char_remove = set([' ','(',')'])
        for row in rows:
            row.email = ''.join([c for c in row.email if c not in char_remove])
            writer.writerow(row)

    print('done. created file: {}'.format(phile))


if __name__ == '__main__':
    args = parser.parse_args()
    who = args.who.lower()
    test = args.test

    if test:
        print(args)

    sys.exit(main())
