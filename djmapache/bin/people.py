# -*- coding: utf-8 -*-

import os, sys
# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djimix.settings')

# required if using django models
import django
django.setup()

from django.conf import settings
from djimix.core.utils import get_connection

import pyodbc
import argparse
import logging

logger = logging.getLogger('djimix')

# set up command-line options
desc = """
Accepts as input a group type: student, faculty, or staff
"""

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    '-w', '--who',
    required=True,
    help="student, faculty, staff",
    dest='who'
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test'
)


def main():
    '''
    main function
    '''

    sql = """
        SELECT
            lastname, firstname, username
        FROM
            provisioning_vw
        WHERE
            {} is not null
        ORDER BY
            lastname, firstname
        LIMIT 10
    """.format(who)

    if test:
        print("sql = {}".format(sql))
        logger.debug("sql = {}".format(sql))
    else:
        connection = get_connection()
        cursor = connection.cursor()
        objects = cursor.execute(sql)
        peeps = []
        for obj in objects:
            gn = obj[1]
            sn = obj[0]
            un = obj[2]
            row = {
                'lastname': sn, 'firstname': gn,
                'email': '{}@carthage.edu'.format(un)
            }
            #row = {
                #'lastname': obj[0], 'firstname': obj[1],
                #'email': '{}@carthage.edu'.format(obj[2])
            #}
            peeps.append(row)
            #print(row['lastname'])
            #print(obj[2],obj[1],obj[d])
            #print(gn,sn,un)
        for p in  peeps:
            for n,v in p.items():
                print(n,v)


if __name__ == '__main__':
    args = parser.parse_args()
    who = args.who
    test = args.test

    if test:
        print(args)

    sys.exit(main())

