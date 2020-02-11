# -*- coding: utf-8 -*-

import argparse
import io
import os
import re
import sys

from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import portrait
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak
from reportlab.platypus import Preformatted
from reportlab.platypus import SimpleDocTemplate
import pysftp


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.shell')


# set up command-line options
desc = """
    Fetch transcripts from our server, generate PDFs based on them,
    and transfer them to scripsafe server.
"""

parser = argparse.ArgumentParser(description=desc)

parser.add_argument(
    '--test',
    action='store_true',
    help='Dry run?',
    dest='test',
)


def paint_pdf(phile):
    """Generate a PDF."""
    buf = io.BytesIO()

    # Setup the document with paper size and margins
    doc = SimpleDocTemplate(
        buf,
        rightMargin=settings.SCRIP_SAFE_RIGHT_MARGIN * inch,
        leftMargin=settings.SCRIP_SAFE_LEFT_MARGIN * inch,
        topMargin=settings.SCRIP_SAFE_TOP_MARGIN * inch,
        bottomMargin=settings.SCRIP_SAFE_BOTTOM_MARGIN * inch,
        pagesize=portrait(letter),
    )

    # Styling
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CodeSmall',
        parent=styles['Code'],
        fontSize=settings.SCRIP_SAFE_FONT_SIZE,
        leading=settings.SCRIPT_SAFE_LEADING,
    ))

    lines = []
    # line break at Page n of n
    reg = re.compile('(Page) (\d+) (of) (\d+)')
    for line in phile.readlines():
        if reg.search(line):
            lines.append(PageBreak())
        lines.append(Preformatted(
            line.decode('cp1252').encode('utf-8'), styles['CodeSmall'],
        ))
    doc.build(lines)

    # Write the PDF to a file
    with open('{0}.pdf'.format(phile.name), 'w') as fd:
        fd.write(buf.getvalue())


def main():
    """Main function for execution from command line."""
    # go to our storage directory on this server
    os.chdir(settings.SCRIP_SAFE_LOCAL_PATH)
    # obtain a list of file names from transcript spool
    philes = []
    with pysftp.Connection(**settings.SCRIP_SAFE_LOCAL_CONNECTION) as sftp:
        sftp.cwd(settings.SCRIP_SAFE_LOCAL_SPOOL)
        for attr in sftp.listdir_attr():
            phile = attr.filename
            if phile.startswith(settings.SCRIP_SAFE_FILE_PREFIX, 0):
                try:
                    sftp.get(phile, preserve_mtime=True)
                    # generate PDFs
                    with open(phile, 'r') as fo:  # safer than w mode
                        paint_pdf(fo)
                    philes.append(phile)
                    # delete original since we have a copy
                    sftp.remove(phile)
                except IOError as ioerror:
                    print("I/O error({0}): {1}".format(
                        ioerror.errno, ioerror.strerror,
                    ))

    if test:
        print("philes = {0}".format(philes))

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # External connection information for Common Application server
    xtrnl_connection = {
        'host': settings.SCRIP_SAFE_XTRNL_SERVER,
        'username': settings.SCRIP_SAFE_XTRNL_USER,
        'private_key': settings.SCRIP_SAFE_XTRNL_KEY,
        'cnopts': cnopts,
    }
    # transfer the PDFs to scripsafe
    with pysftp.Connection(**xtrnl_connection) as sftpx:
        for pdf in philes:
            if test:
                print("putting {0}.pdf".format(pdf))
            sftpx.put('{0}.pdf'.format(pdf), preserve_mtime=True)

    # backup and cleanup
    with pysftp.Connection(**settings.SCRIP_SAFE_LOCAL_CONNECTION) as sftpl:
        for pdfbak in philes:
            sftpl.cwd(settings.SCRIP_SAFE_LOCAL_BACKUP)
            # copy transcripts to archive
            try:
                sftpl.put(pdfbak, preserve_mtime=True)
            except Exception as error:
                print('failed to put file to local backup: {0}. {1}'.format(
                    pdfbak, error,
                ))

            # remove files fetched from local server and generated PDFs
            if not test:
                try:
                    os.remove(pdfbak)
                    os.remove('{0}.pdf'.format(pdfbak))
                    print("removed files: {0}, {1}.pdf".format(pdfbak, pdfbak))
                except OSError as oserror:
                    print("failed to remove files from local file system")
                    print("{0} {1}".format(pdfbak, oserror))

    print("files sent to script safe:\n{0}".format(philes))


if __name__ == '__main__':
    args = parser.parse_args()
    test = args.test

    sys.exit(main())
