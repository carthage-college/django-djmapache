# -*- coding: utf-8 -*-

import os, sys
# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.shell')

# required if using django models
import django
django.setup()

from django.conf import settings
from djimix.core.utils import get_connection

import pyodbc
import argparse
import logging

logger = logging.getLogger('djmapache')

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
    main function:

    Last Name
    First Name
    Preferred (Nick) Name
    Previous Last Name
    Carthage Email
    Carthage ID
    User Type

    '''

    sql = '''
        SELECT
            provisioning_vw.lastname, provisioning_vw.firstname,
            TRIM(aname_rec.line1) as alt_name,
            TRIM(NVL(maiden.lastname,"")) AS birth_last_name,
            provisioning_vw.username, provisioning_vw.id AS cid,
        FROM
            provisioning_vw
        LEFT JOIN (
            SELECT
                prim_id, MAX(active_date) active_date
            FROM
                addree_rec
            WHERE
                style = "M"
            GROUP BY prim_id
            )
            prevmap
        ON
            provisioning_vw.id = prevmap.prim_id
        LEFT JOIN
            addree_rec maiden
        ON
            maiden.prim_id = prevmap.prim_id
        AND
            maiden.active_date = prevmap.active_date
        AND
            maiden.style = "M"
        LEFT JOIN
            aa_rec AS aname_rec
        ON
            (provisioning_vw.id = aname_rec.id AND aname_rec.aa = "ANDR")
        WHERE
            provisioning_vw.{} is not null
        ORDER BY
            provisioning_vw.lastname, provisioning_vw.firstname
        LIMIT 10
    '''.format(who)

    if test:
        print("sql = {}".format(sql))
        logger.debug("sql = {}".format(sql))
    else:
        connection = get_connection()
        cursor = connection.cursor()
        objects = cursor.execute(sql)
        peeps = []
        for obj in objects:
            row = {
                'last_name': obj.lastname, 'first_name': obj.firstname,
                'preferred_name': obj.preferred_name,
                'birth_last_name': obj.birth_last_name,
                'email': '{}@carthage.edu'.format(obj.username),
                'cid': obj.cid, 'user_type': who
            }
            peeps.append(row)
        for p in  peeps:
            print(p)


if __name__ == '__main__':
    args = parser.parse_args()
    who = args.who
    test = args.test

    if test:
        print(args)

    sys.exit(main())

