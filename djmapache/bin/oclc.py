# -*- coding: utf-8 -*-

import pysftp
import io
import os
import sys

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.template import loader
from djimix.core.utils import get_connection
from djimix.core.utils import xsql
from djtools.fields import NOW


# django settings for shell environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.shell')

# required because we are using django templates
import django
django.setup()

# informix environment
os.environ['INFORMIXSERVER'] = settings.INFORMIXSERVER
os.environ['DBSERVERNAME'] = settings.DBSERVERNAME
os.environ['INFORMIXDIR'] = settings.INFORMIXDIR
os.environ['ODBCINI'] = settings.ODBCINI
os.environ['ONCONFIG'] = settings.ONCONFIG
os.environ['INFORMIXSQLHOSTS'] = settings.INFORMIXSQLHOSTS
os.environ['LD_LIBRARY_PATH'] = settings.LD_LIBRARY_PATH
os.environ['LD_RUN_PATH'] = settings.LD_RUN_PATH

NEXT_YEAR = NOW + relativedelta(years=1)


def main():
    """OCLC Synchronization."""
    folks = []
    phile = os.path.join(
        settings.BASE_DIR, 'sql/oclc/student_facstaff.sql',
    )
    with open(phile) as incantation:
        sql = incantation.read()

    with get_connection() as connection:
        rows = xsql(sql, connection, key=settings.INFORMIX_DEBUG).fetchall()

    for row in rows:
        folks.append({
            'lastname': row.lastname,
            'firstname': row.firstname,
            'middlename': row.middlename,
            'id': row.id,
            'addr_line1': row.addr_line1,
            'addr_line2': row.addr_line2,
            'city': row.city,
            'st': row.st,
            'ctry': row.ctry,
            'zip': row.zip,
            'phone': row.phone,
            'email': row.email,
            'groupIndex': row[settings.OCLC_GROUPINDEX_LIST_INDEX],
            'grouping': row.grouping,
            'expirationDate': row.expirationdate,
        })
    template = loader.get_template('oclc/personas.xml')
    xml = template.render({'objs': folks, 'next_year': NEXT_YEAR})
    xml_path = "{0}carthage_personas_draft_{1:%Y-%m-%d}.xml".format(
        settings.OCLC_LOCAL_PATH, NOW,
    )

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    xtrnl_connection = {
        'host': settings.OCLC_XTRNL_SRVR,
        'username': settings.OCLC_XTRNL_USER,
        'password': settings.OCLC_XTRNL_PASS,
        'cnopts': cnopts,
    }

    with io.open(xml_path, 'w', encoding='utf8') as xml_file:
        xml_file.write(xml)

    xfile = "carthage_personas_draft_{0:%Y-%m-%d}.xml".format(NOW)
    with pysftp.Connection(**xtrnl_connection) as sftp:
        sftp.cwd(settings.OCLC_XTRNL_PATH)
        sftp.put(xml_path, xfile)
        sftp.close()


if __name__ == '__main__':

    sys.exit(main())
