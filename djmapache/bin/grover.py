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
from djmapache.sql.grover import ALUMNI, FACSTAFF_STUDENT
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

    headers = [
        'User Type','Email Address','Database Key','First Name','Last Name',
        'Preferred Name','Previous Last Name',
        'Transcript First Name','Transcript Last Name',
        'Concentration','Majors Admin Only','Minors Admin Only',
        'Social Class Year','Grad Year'
    ]
    diplo_fields = ''
    diplo_join = ''
    if who == 'student' or who == 'faculty' or who == 'staff':
        if who == 'student':
            diplo_fields = '''
                TRIM(diplo.firstname) as diploma_firstname,
                TRIM(diplo.lastname) as diploma_lastname,
            '''
            diplo_join = '''
                LEFT JOIN
                    addree_rec diplo
                ON
                    provisioning_vw.id = diplo.prim_id
                AND
                    diplo.style= "D"
                AND
                    NVL(diplo.inactive_date, TODAY) >= TODAY
            '''
            where = '''
                provisioning_vw.student IS NOT NULL
                AND
                prog_enr_rec.lv_date IS NULL
            '''
        elif who =='faculty':
            where = 'provisioning_vw.faculty IS NOT NULL'
        elif who == 'staff':
            where = 'provisioning_vw.staff IS NOT NULL'
        else:
            print("wa?\n")
            exit(-1)
        sql = FACSTAFF_STUDENT(who, diplo_fields, diplo_join, where)
    elif who == 'alumni':
        sql = ALUMNI
    else:
        print("who must be: 'student', 'faculty', 'staff', or 'alumni'\n")
        exit(-1)

    if test:
        print(headers)
        print("sql = {}".format(sql))
        logger.debug("sql = {}".format(sql))
        exit(-1)

    connection = get_connection()
    with connection:
        rows = xsql(sql, connection).fetchall()
    with open(r'grover.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([x for x in headers])
        for row in rows:
            row.username = '{}@carthage.edu'.format(row.username)
            writer.writerow(row)

    print('done.')


if __name__ == '__main__':
    args = parser.parse_args()
    who = args.who
    test = args.test

    if test:
        print(args)

    sys.exit(main())
