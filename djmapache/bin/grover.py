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


def _whoareyou(mail,cid,fn,sn,wtype,tag,pn,bn,yr):
    who = None
    if wtype == 'faculty' or wtype == 'staff':
        who = f'{mail}|{cid}|{fn}|{sn}|{wtype}|{tag}|{pn}|{bn}'
    elif wtype == 'student':
        who = f'{mail}|{cid}|{fn}|{sn}|{wtype}|{tag}|{pn}|{bn}|{yr}'
    return who


def main():
    '''
    CSV headers:
    Email|Database Key|First Name|Last Name|User Type|User Tags|etc...

    User data:
    Last Name
    First Name
    Preferred (Nick) Name
    Previous Last Name
    Carthage Email
    Carthage ID
    User Type
    '''

    grad_yr_field = ''
    grad_yr_join = ''
    grad_yr_where = ''
    if who == 'student':
        grad_yr_field = 'prog_enr_rec.plan_grad_yr,'
        grad_yr_join = '''
            LEFT JOIN
                prog_enr_rec
            ON
                provisioning_vw.id = prog_enr_rec.id
        '''
        grad_yr_where = '''
            AND prog_enr_rec.lv_date is null AND prog_enr_rec.plan_grad_yr != 0
        '''

    sql = '''
        SELECT
            provisioning_vw.lastname, provisioning_vw.firstname,
            TRIM(aname_rec.line1) as alt_name,
            TRIM(NVL(maiden.lastname,"")) AS birth_last_name,
            provisioning_vw.username, {}
            provisioning_vw.id AS cid
        FROM
            provisioning_vw
        {}
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
            prevmap.prim_id = maiden.prim_id
        AND
            prevmap.active_date = maiden.active_date
        AND
            maiden.style = "M"
        LEFT JOIN
            aa_rec AS aname_rec
        ON
            (provisioning_vw.id = aname_rec.id AND aname_rec.aa = "ANDR")
        WHERE
            provisioning_vw.{} is not null
        {}
        ORDER BY
            provisioning_vw.lastname, provisioning_vw.firstname
    '''.format(grad_yr_field, grad_yr_join, who, grad_yr_where)

    if test:
        print("sql = {}".format(sql))
        logger.debug("sql = {}".format(sql))
    connection = get_connection()
    cursor = connection.cursor()
    objects = cursor.execute(sql)
    peeps = []
    for o,obj in enumerate(objects):
        grad_yr = None
        if who == 'student':
            grad_yr = obj.plan_grad_yr
        row = _whoareyou(
            '{}@carthage.edu'.format(obj.username),obj.cid,obj.firstname,
            obj.lastname,who,'Soft Launch {}'.format(who.capitalize()),
            obj.alt_name,obj.birth_last_name,grad_yr
        )
        if test:
            print('{}) {}'.format(o,row))
        else:
            print('{}'.format(row))

if __name__ == '__main__':
    args = parser.parse_args()
    who = args.who
    test = args.test

    if test:
        print(args)

    sys.exit(main())

