# -*- coding: utf-8 -*-

import os, sys
# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.shell')

# required if using django models
import django
django.setup()

from django.conf import settings

from djmapache.sql.grover import ALUMNI, FACSTAFF_STUDENT

from djimix.core.utils import get_connection

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


def _whoareyou(mail,cid,fn,sn,wtype,tag,pn,bn,ayr='',gyr='',syr=''):
    who = None
    if not gyr:
        gyr = ''
    if not syr:
        syr = ''
    if wtype == 'faculty' or wtype == 'staff':
        who = f'{mail}|{cid}|{fn}|{sn}|{wtype}|{tag}|{pn}|{bn}'
    elif wtype == 'student':
        who = f'{mail}|{cid}|{fn}|{sn}|{wtype}|{tag}|{pn}|{bn}|{ayr}'
    elif wtype == 'alumni':
        who = f'{mail}|{cid}|{fn}|{sn}|{wtype}|{tag}|{pn}|{bn}|{gyr}|{syr}'

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

    if who == 'facstaff' or who == 'student':
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
        sql = FACSTAFF_STUDENT(grad_yr_field, grad_yr_join, who, grad_yr_where)
        headers = "Email|Database Key|First Name|Last Name|User Type|User Tags"
        if who == 'student':
            headers += "|Anticipated Grad Year"
    elif who == 'alumni':
        sql = ALUMNI
        headers = "Email|Database Key|First Name|Last Name|User Type|User Tags|Graduation Year|social class year"
    else:
        print("who must be: 'facstaff', 'student', or 'alumni'\n")
        exit(-1)

    if test:
        print("sql = {}".format(sql))
        logger.debug("sql = {}".format(sql))

    connection = get_connection()
    cursor = connection.cursor()
    objects = cursor.execute(sql)

    print(headers)
    peeps = []
    for o,obj in enumerate(objects):
        if obj.email1 or obj.email2:
            email = obj.email2
            if not email:
                email = obj.email1
            ayr = ''
            if who == 'alumni':
                row = _whoareyou(
                    email,obj.cid,obj.firstname,obj.lastname,
                    who,'Soft Launch {}'.format(who.capitalize()),
                    obj.alt_name,obj.birth_last_name,ayr,obj.grad_yr,obj.soc_yr
                )
            else:
                if who == 'student':
                    ayr = obj.plan_grad_yr
                row = _whoareyou(
                    '{}@carthage.edu'.format(obj.username),obj.cid,obj.firstname,
                    obj.lastname,who,'Soft Launch {}'.format(who.capitalize()),
                    obj.alt_name,obj.birth_last_name,ayr
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

