# -*- coding: utf-8 -*-

import argparse
import csv
import django
import json
import logging
import os
import sys


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.shell')

# required if using django models
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
    '--pseudo',
    action='store_true',
    help="Include pseudo alumni?",
    dest='pseudo'
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
    'Social Class Year','Graduation Year'
]
HEADERS['education'] = [
    'Database Key','Email Address','School Name','School Degree',
    'School Major(s)','School Minor','School Year'
]


def main():

    # check for profile type will fail if not one of the four allowed types
    try:
        headers = HEADERS[who]
    except:
        print("who must be: 'student', 'facstaff', 'alumni', or 'education'\n")
        print("who = {}".format(who))
        exit(-1)

    suffix = ''
    if pseudo:
        suffix = '_pseudo'

    phile = os.path.join(settings.BASE_DIR, 'sql/grover', '{}{}.sql'.format(
        who, suffix
    ))
    with open(phile) as incantation:
        sql = incantation.read()

    if test:
        print("who = {}".format(who))
        print("headers")
        print(headers)
        print("phile:")
        print(phile)
        print("sql = {}".format(sql))
        logger.debug("sql = {}".format(sql))
        exit(-1)

    connection = get_connection()
    with connection:
        rows = xsql(sql, connection, key=settings.INFORMIX_DEBUG).fetchall()

    phile = r'{}{}.csv'.format(who, suffix)
    with open(phile, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_NONE, quotechar='')
        writer.writerow([x for x in headers])
        char_remove = set([' ','(',')'])
        for row in rows:
            # sometimes the provisioning view will include an entity that was
            # just created and might not have a username just yet.
            if row.email:
                row.email = ''.join([c for c in row.email if c not in char_remove])
            # grover's import app does not like trailing commas in the list.
            # python 3 returns an iterator from filter(), so we wrap it in list()
            # grover also wants double quotes and not single quotes so we
            # convert the list to json string with dumps()
            if who != 'facstaff':
                if who != 'education':
                    concentration = list(filter(None, row.concentration.split(',')))
                    row.concentration = json.dumps(concentration)
                majors = list(filter(None, row.majors.split(',')))
                row.majors = json.dumps(majors)
                minors = list(filter(None, row.minors.split(',')))
                row.minors = json.dumps(minors)
            # write the row
            writer.writerow(row)

    print('done. created file: {}'.format(phile))


if __name__ == '__main__':
    args = parser.parse_args()
    who = args.who.lower()
    pseudo = args.pseudo
    test = args.test

    if test:
        print(args)

    sys.exit(main())
