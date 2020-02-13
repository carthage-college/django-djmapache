# -*- coding: utf-8 -*-
import os
import sys
import argparse

# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.shell')

from django.conf import settings

# informix environment
os.environ['INFORMIXSERVER'] = settings.INFORMIXSERVER
os.environ['DBSERVERNAME'] = settings.DBSERVERNAME
os.environ['INFORMIXDIR'] = settings.INFORMIXDIR
os.environ['ODBCINI'] = settings.ODBCINI
os.environ['ONCONFIG'] = settings.ONCONFIG
os.environ['INFORMIXSQLHOSTS'] = settings.INFORMIXSQLHOSTS
os.environ['LD_LIBRARY_PATH'] = settings.LD_LIBRARY_PATH
os.environ['LD_RUN_PATH'] = settings.LD_RUN_PATH

from djimix.core.utils import get_connection, xsql

import csv

# set up command-line options
desc = """
    updates the class_year table,
    setting it to 0 where it equals 9999
"""

parser = argparse.ArgumentParser(description=desc)

parser.add_argument(
    '-a', '--action',
    help='select or update.',
    dest='action'
)
parser.add_argument(
    '-d', '--database',
    help='database name.',
    dest='database'
)
parser.add_argument(
    '--test',
    action='store_true',
    help='Dry run?',
    dest='test'
)


def main():
    """Main function."""
    if database == 'jxtest':
        EARL = settings.INFORMIX_ODBC_JXTEST
    elif database == 'jxlive':
        EARL = settings.INFORMIX_ODBC_JXPROD
    else:
        EARL = None

    if test:
        print(EARL)

    connection = get_connection(EARL)
    with connection:
        if action == 'update':
            sql = '''
                UPDATE
                    class_year
                SET
                    class_year=0
                WHERE
                    class_year=9999
            '''
            if test:
                print(sql)
            else:
                xsql(sql, connection, key=settings.INFORMIX_DEBUG)
        elif action == 'select':
            sql = '''
                SELECT
                    *
                FROM
                    class_year
                WHERE
                    class_year=9999
            '''
            rows = xsql(sql, connection, key=settings.INFORMIX_DEBUG)
            years = rows.fetchall()
            for y in years:
                print(y)
        else:
            print('how did that happen?')
            sys.exit()


if __name__ == "__main__":
    args = parser.parse_args()
    action = args.action
    database = args.database
    test = args.test

    if not action or not database:
        print("mandatory options are missing: database and action\n")
        parser.print_help()
        exit(-1)
    else:
        action = action.lower()
        database = database.lower()

    if database != 'jxlive' and database != 'jxtest':
        print("database must be: 'jxlive' or 'jxtest'\n")
        parser.print_help()
        exit(-1)

    if action != 'select' and action != 'update':
        print("action must be: 'select' or 'update'\n")
        parser.print_help()
        exit(-1)

    sys.exit(main())
