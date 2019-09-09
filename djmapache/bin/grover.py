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
    '-d', '--data',
    required=True,
    help="'user' or 'education' data",
    dest='data'
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

# global for data type
data=None


def _whoareyou(mail,cid,fn,sn,pn,bn,wtype,tag,gyr,syr):
    '''
    mail = email
    cid = college id
    fn = first name
    sn = surname
    pn = previous name
    bn = birth name
    wtype = who
    tag = system tags
    gyr = graduation year
    syr = social class year
    '''

    who = None
    if not gyr:
        gyr = ''
    if not syr:
        syr = ''
    if data == 'education':
        who = f'{mail}|{cid}|Carthage College|{tag}|{gyr}'
    else:
        if wtype == 'alumni':
            who = f'{mail}|{cid}|{fn}|{sn}|{pn}|{wtype}|{tag}|{syr}'
        else:
            who = f'{mail}|{cid}|{fn}|{sn}|{pn}|{wtype}|{tag}'

    return who


def main():
    '''
    CSV Headers

    User data:
    Email
    Database Key (College ID)
    First Name
    Last Name
    Preferred Name
    User Type
    User Tag
    Social Class Year

    Education data:
    Email
    Database Key (College ID)
    School

    ?
    Previous Last Name
    '''

    if data == 'user':
        headers = "Email|Database Key|First Name|Last Name|Preferred Name|User Type|User Tags"
    elif data == 'education':
        headers = "Email|Database Key|School|Graduation Year|User Tags"
    else:
        print("data must be: 'user' or 'education'\n")
        exit(-1)

    where = '''
        provisioning_vw.faculty IS NOT NULL OR
        provisioning_vw.staff IS NOT NULL
    '''

    if who == 'facstaff' or who == 'student':
        grad_yr_field = '"" as grad_yr,'
        grad_yr_join = ''
        grad_yr_where = ''
        if who == 'student':
            grad_yr_field = 'prog_enr_rec.plan_grad_yr as grad_yr,'
            grad_yr_join = '''
                LEFT JOIN
                    prog_enr_rec
                ON
                    provisioning_vw.id = prog_enr_rec.id
            '''
            grad_yr_where = '''
                AND prog_enr_rec.lv_date IS NULL
                AND prog_enr_rec.plan_grad_yr != 0
            '''
            where = 'provisioning_vw.student IS NOT NULL'
        sql = FACSTAFF_STUDENT(grad_yr_field, grad_yr_join, where, grad_yr_where)
    elif who == 'alumni':
        sql = ALUMNI
        if data == 'user':
            headers += "|social class year"
    else:
        print("who must be: 'facstaff', 'student', or 'alumni'\n")
        print("data must be: 'user', 'education''\n")
        exit(-1)

    print(headers)

    if test:
        print("sql = {}".format(sql))
        logger.debug("sql = {}".format(sql))
        exit(-1)

    connection = get_connection()
    cursor = connection.cursor()
    objects = cursor.execute(sql)

    peeps = []
    for o,obj in enumerate(objects):
        email = '{}@carthage.edu'.format(obj.username)
        if who == 'alumni':
            email = obj.email2
            if not email:
                email = obj.email1

        tag = 'Soft Launch {} {}'.format(who.capitalize(),data.capitalize())
        row = _whoareyou(
            email,obj.cid,obj.firstname,obj.lastname,obj.alt_name,
            obj.birth_last_name,who,tag,obj.grad_yr,obj.soc_yr
        )

        if test:
            print('{}) {}'.format(o,row))
        else:
            print('{}'.format(row))


if __name__ == '__main__':
    args = parser.parse_args()
    who = args.who
    data = args.data
    test = args.test

    if test:
        print(args)

    sys.exit(main())
