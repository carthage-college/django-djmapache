import os
import sys
# import pysftp
import csv
import argparse
import logging
from logging.handlers import SMTPHandler
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djmapache.settings.shell")
django.setup()
from django.conf import settings


import openpyxl
from openpyxl import Workbook
from django.conf import settings
from djimix.core.utils import get_connection, xsql
from djmapache.workday.hcm_hr.utilities import fn_format_country, \
    fn_write_addr_cl_header, fn_write_addr_cl, fn_get_id


# informix environment
os.environ['INFORMIXSERVER'] = settings.INFORMIXSERVER
os.environ['DBSERVERNAME'] = settings.DBSERVERNAME
os.environ['INFORMIXDIR'] = settings.INFORMIXDIR
os.environ['ODBCINI'] = settings.ODBCINI
os.environ['ONCONFIG'] = settings.ONCONFIG
os.environ['INFORMIXSQLHOSTS'] = settings.INFORMIXSQLHOSTS
os.environ['LD_LIBRARY_PATH'] = settings.LD_LIBRARY_PATH
os.environ['LD_RUN_PATH'] = settings.LD_RUN_PATH

# # normally set as 'debug" in SETTINGS
# DEBUG = settings.INFORMIX_DEBUG

# set up command-line options
desc = """
    Upload ADP data to CX
"""
parser = argparse.ArgumentParser(description=desc)

parser.add_argument(
    "--test",
    action='store_true',
    help="Dry run?",
    dest="test"
)
parser.add_argument(
    "-d", "--database",
    help="database name.",
    dest="database"
)
#
# def file_download():
#     if test:
#         adp_csv_output = "/home/dsullivan/djlabour/djlabour/testdata/"
#     else:
#         adp_csv_output = settings.ADP_CSV_OUTPUT
#     # sFTP fetch (GET) downloads the file from ADP file from server
#     # print("Get ADP File")
#     cnopts = pysftp.CnOpts()
#     cnopts.hostkeys = None
#     # cnopts.hostkeys = settings.ADP_HOSTKEY
#     # External connection information for ADP Application server
#     XTRNL_CONNECTION = {
#        'host': settings.ADP_HOST,
#        'username': settings.ADP_USER,
#        'password': settings.ADP_PASS,
#        'cnopts': cnopts
#     }
#     with pysftp.Connection(**XTRNL_CONNECTION) as sftp:
#         try:
#             # print('Connection Established')
#             sftp.chdir("adp/")
#             # Remote Path is the ADP server and once logged in we fetch
#             # directory listing
#             remotepath = sftp.listdir()
#             # Loop through remote path directory list
#             # print("Remote Path = " + str(remotepath))
#             for filename in remotepath:
#                 remotefile = filename
#                 # print("Remote File = " + str(remotefile))
#                 # set local directory for which the ADP file will be
#                 # downloaded to
#                 local_dir = ('{0}'.format(
#                     adp_csv_output
#                 ))
#                 localpath = local_dir + remotefile
#                 # GET file from sFTP server and download it to localpath
#                 sftp.get(remotefile, localpath)
#                 #############################################################
#                 # Delete original file %m_%d_%y_%h_%i_%s_Applications(%c).txt
#                 # from sFTP (ADP) server
#                 #############################################################
#                 # sftp.remove(filename)
#         except Exception as e:
#             # print("Error in address.py- File download, " + e.message)
#             fn_write_error("Error in address.py - File download, "
#                            "adptocx.csv not found, " +  repr(e))
#             fn_send_mail(settings.ADP_TO_EMAIL, settings.ADP_FROM_EMAIL,
#                 "Error in address.py - File download, "
#                 "adptocx.csv not found," + repr(e),
#                 "Error in address.py - File download")
#
#     sftp.close()


def fn_clear_sheet(email_csv_output, new_xl_file):
    wb_obj = openpyxl.load_workbook(email_csv_output + new_xl_file)
    this_sheet = wb_obj['Address']
    print(this_sheet)
    row_count = this_sheet.max_row
    col_count = this_sheet.max_column
    print(row_count)
    print(col_count)

    for row in this_sheet['A3:N' + str(row_count)]:
        # print(row)
        for cell in row:
            # print(cell.value)
            cell.value = ""
            # print(cell.value)

    wb_obj.save(email_csv_output + new_xl_file)

def fn_insert_xl(ct, workerid, cntry, addr_typ, addr_use, region, subregion,
                 city, city_subdv, postal_cod, addr1, addr2, addr3, addr4,
                 rem_ee,
                 csv_output, new_xl_file):
    try:
        wb_obj = openpyxl.load_workbook(csv_output
                                        + new_xl_file)
        # this may be the syntax to open a pwd protected xls..
        # wb_obj.protection.password = ''
        # After a fair amount of research, it seems that there is no easy
        # way to use a password withing Python to pass to an Excel file
        # May be easiest just to remove the password protection and re-enter
        # it when the work is done.

        # # print(wb_obj.sheetnames)
        this_sheet = wb_obj['Address']
        # print(this_sheet)
        this_sheet.cell(row=ct, column=1).value = workerid
        this_sheet.cell(row=ct, column=2).value = cntry
        this_sheet.cell(row=ct, column=3).value = addr_typ
        this_sheet.cell(row=ct, column=4).value = addr_use
        this_sheet.cell(row=ct, column=5).value = region
        this_sheet.cell(row=ct, column=6).value = subregion
        this_sheet.cell(row=ct, column=7).value = city

        this_sheet.cell(row=ct, column=8).value = city_subdv
        this_sheet.cell(row=ct, column=9).value = postal_cod
        this_sheet.cell(row=ct, column=10).value = addr1
        this_sheet.cell(row=ct, column=11).value = addr2
        this_sheet.cell(row=ct, column=12).value = addr3
        this_sheet.cell(row=ct, column=13).value = addr4
        this_sheet.cell(row=ct, column=14).value = rem_ee

        wb_obj.save(csv_output + new_xl_file)

    except Exception as e:
        print("Error in address.py fn_ins_xl , Error = " + repr(e))
    # fn_write_error("Error in address.py - fn_get_id: "
    #                + repr(e))
    # fn_send_mail(settings.ADP_TO_EMAIL, settings.ADP_FROM_EMAIL,
    #          "Error in address.py fn_get_id, Error = " + repr(e),
    #          "Error in address.py fn_get_id")

def main():

    ##########################################################################
    # ==> python phone_rec.py --database=train --test
    # ==> python phone_rec.py --database=cars
    ##########################################################################

    # # Defines file names and directory location
    # if test:
    csv_output = "/home/dsullivan/djmapache/djmapache/workday/hcm_hr/" \
                            "clean_data/"
    csv_input = "/home/dsullivan/djmapache/djmapache/workday/hcm_hr/" \
                             "raw_data/"
    # else:
    # csv_output = settings.csv_output
    # print(csv_output)

    # For testing use last file
    # new_file = csv_output + "ADPtoCXLast.csv"
    raw_file = csv_input + "addresses.csv"
    new_file = csv_output + "address_cln.csv"
    new_xl_file = "Worker Data.xlsx"

    fn_clear_sheet(csv_output, new_xl_file)

    try:
        # set global variable
        global EARL
        # determines which database is being called from the command line
        if database == 'cars':
            EARL = settings.INFORMIX_ODBC
        if database == 'train':
            EARL = settings.INFORMIX_ODBC_TRAIN
        else:
            # # this will raise an error when we call get_engine()
            # below but the argument parser should have taken
            # care of this scenario and we will never arrive here.
            EARL = None
            # establish database connection
        # print(EARL)

        # Pull the file from the ADP FTP site
        # execute sftp code in production only
        # if not test:
        #     file_download()

        # Create the new csv file for the formatted data
        fn_write_addr_cl_header(new_file)

        # Read the raw file and work on the formatting
        # print(raw_file)
        with open(raw_file, 'r') as f:
            d_reader = csv.DictReader(f, delimiter=',')
            ct = 2  # Leave at 1 to skip the header row...
            r = 0
            # Write to Excel spreadsheet

            for row in d_reader:
                # print("+++++++++++++++++++++")
                # print(row)
                r = r+1
                # print("ROW " + str(r))
                # print("Inserts " + str(ct))

                """Student workers and a few others typically 
                don't have the
                    Carthage ID Custom field populated  May have 
                    to force it
                    here"""
                if row['Carthage ID #'] == "":
                #     print('No Carth ID  ' + row['File Number'])
                    if row['File Number'] == "":
                        print("No id or file number")
                        pass
                    else:
                        # print(str(row['File Number']))
                        workerid = fn_get_id(str(row['File Number']), EARL,
                                            settings.INFORMIX_DEBUG)
                        # print(workerid)
                else:
                    workerid = row['Carthage ID #']
                    # print(workerid)

                """Format country and phone - I don't know if our 
                ADP  data
                    has any phone numbers that aren't in the US 
                    format"""

                cntry = fn_format_country(row['Primary Address: Country Code'])
                # cntry = row['Primary Address: Country Code']
                addr_typ = "Primary Home"
                addr_use = "Other - Home"
                region = row["Primary Address: State / Territory Code"]
                subregion = ""
                city = row["Primary Address: City"]
                city_subdv = ""
                postal_cod = row["Primary Address: Zip / Postal Code"]
                addr1 = row["Primary Address: Address Line 1"]
                addr2 = row["Primary Address: Address Line 2"]
                addr3 = ""
                addr4 = ""

                # Not sure how to populate this...
                remote_EE = ""

                # print(workerid, cntry, addr_typ, addr_use, region, city,
                #       postal_cod, addr1, addr2)

                if row["Primary Address: Country Code"] == 'USA':
                    fn_write_addr_cl(new_file, [workerid + ',' + cntry + ','
                        + addr_typ + ',' + addr_use + ',' + region + ','
                        + subregion + ',' + city + ',' + city_subdv + ','
                        + postal_cod + ',' + addr1 + ',' + addr2 + ','
                        + addr3 + ',' + addr4 + ',' + remote_EE])
                    ct = ct + 1

                    fn_insert_xl(ct, workerid, cntry, addr_typ, addr_use,
                        region, subregion, city, city_subdv, postal_cod,
                        addr1, addr2, addr3, addr4,  remote_EE,
                        csv_output, new_xl_file)

    except Exception as e:
        print("Error in address.py, Error = " + repr(e))
        # fn_write_error("Error in address.py - Main: "
        #                + repr(e))
        # fn_send_mail(settings.ADP_TO_EMAIL, settings.ADP_FROM_EMAIL,
        #          "Error in address.py, Error = " + repr(e),
        #          "Error in address.py")

if __name__ == "__main__":
    args = parser.parse_args()
    test = args.test
    database = args.database

    if not database:
        print("mandatory option missing: database name\n")
        exit(-1)
    else:
        database = database.lower()

    if database != 'cars' and database != 'train' and database != 'sandbox':
        print("database must be: 'cars' or 'train' or 'sandbox'\n")
        parser.print_help()

    sys.exit(main())
