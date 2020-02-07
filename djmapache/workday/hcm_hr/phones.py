import os
import sys
# import pysftp
import csv
import codecs
import argparse
import logging
from logging.handlers import SMTPHandler

# prime django
import django

# django settings for shell environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djlabour.settings.shell")
django.setup()

# django settings for script
from django.conf import settings
from djimix.core.utils import get_connection, xsql
# from djlabour.sql.phone_sql import CX_VIEW_SQL, Q_phone_VERIFY, \
#     INS_phone_REC
# from djlabour.core.phone_utilities import fn_write_adp_header, \
#     fn_write_header, fn_write_row_reformatted, fn_write_error, fn_send_mail

# informix environment
os.environ['INFORMIXSERVER'] = settings.INFORMIXSERVER
os.environ['DBSERVERNAME'] = settings.DBSERVERNAME
os.environ['INFORMIXDIR'] = settings.INFORMIXDIR
os.environ['ODBCINI'] = settings.ODBCINI
os.environ['ONCONFIG'] = settings.ONCONFIG
os.environ['INFORMIXSQLHOSTS'] = settings.INFORMIXSQLHOSTS
os.environ['LD_LIBRARY_PATH'] = settings.LD_LIBRARY_PATH
os.environ['LD_RUN_PATH'] = settings.LD_RUN_PATH

# normally set as 'debug" in SETTINGS
DEBUG = settings.INFORMIX_DEBUG

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
#             # print("Error in phone_rec.py- File download, " + e.message)
#             fn_write_error("Error in phone_rec.py - File download, "
#                            "adptocx.csv not found, " +  repr(e))
#             fn_send_mail(settings.ADP_TO_EMAIL, settings.ADP_FROM_EMAIL,
#                 "Error in phone_rec.py - File download, "
#                 "adptocx.csv not found," + repr(e),
#                 "Error in phone_rec.py - File download")
# 
#     sftp.close()


def main():

    ##########################################################################
    # ==> python phone_rec.py --database=train --test
    # ==> python phone_rec.py --database=cars
    ##########################################################################

    # # Defines file names and directory location
    # if test:
    phone_csv_output = "/home/dsullivan/djlmapache/djlmapache/workday/hcm_hr/cleandata/"
    phone_csv_input = "/home/dsullivan/djmapache/djmapache/workday/hcm_hr/raw_data/"
    # else:
    # phone_csv_output = settings.phone_csv_output
    # print(phone_csv_output)


    # For testing use last file
    # new_phone_file = phone_csv_output + "ADPtoCXLast.csv"
    raw_phone_file = phone_csv_input + "phones.csv"
    new_phone_file = phone_csv_output + "phones_cln.csv"

    # First remove yesterdays file of updates

    try:
        # # set global variable
        # global EARL
        # # determines which database is being called from the command line
        # if database == 'cars':
        #     EARL = settings.INFORMIX_ODBC
        # if database == 'train':
        #     EARL = settings.INFORMIX_ODBC_TRAIN
        # else:
        #     # # this will raise an error when we call get_engine()
        #     # below but the argument parser should have taken
        #     # care of this scenario and we will never arrive here.
        #     EARL = None
        #     # establish database connection
        # # print(EARL)

        #################################################################
        # STEP 0--
        # Pull the file from the ADP FTP site
        # execute sftp code in production only
        #################################################################
        # if not test:
        #     file_download()

        #################################################################
        # STEP 1--
        # Create the new file for the formatted data
        #################################################################
        # fn_write_phone_cl_header(adptocx_reformatted)
        # Header for new file = "Worker ID", "Phone Type", "Country (Phone)",
        # "International Phone Code", "Area Code", "Phone Number",
        # "Phone Extension", "Public"

        #################################################################
        # STEP 2--
        # Read the raw file and work on the formatting
        #################################################################
        # print(raw_phone_file)

        with open(raw_phone_file, 'r') as f:
            d_reader = csv.DictReader(f, delimiter=',')
            for row in d_reader:
                # print("+++++++++++++++++++++")
                # print(row)

                """Student workers and a few others typically don't have the
                    Carthage ID Custom field populated  May have to force it
                    here"""
                if row['Carthage ID #'] == "":
                #     print('No Carth ID  ' + row['File Number'])
                    if row['File Number'] == "":
                        print("No id or file number")
                        pass
                    else:
                        workerid = "1" + row['File Number']
                else:
                    workerid = row['Carthage ID #']

                """Format country and phone - I don't know if our ADP  data 
                    has any phone numbers that aren't in the US format"""

                if row['Primary Address: Country Code'] == "USA":
                    cntry = 'United States of America'
                    intlcode = "1"
                elif row['Primary Address: Country Code'] == "CAN":
                    cntry = 'Canada'
                    intlcode = "1"
                elif row['Primary Address: Country Code'] == "CHN":
                    cntry = 'China'
                elif row['Primary Address: Country Code'] == "DEU":
                    cntry = 'German'
                elif row['Primary Address: Country Code'] == "SRB":
                    cntry = 'Serbia'
                else:
                    cntry = ""
                    area = ""
                    phon = ""
                    print(workerid + " Country unclear")


                if row['Personal Contact: Home Phone'] != "":
                    area = row['Personal Contact: Home Phone'][1:4]
                    phon = row['Personal Contact: Home Phone'][6:14]
                    print(workerid + ',' + "Home" + ','
                          + cntry + ',' + intlcode + ',' + area + ',' + phon
                          + ',' + 'Phone Extension' + ',' + 'Public')

                if row['Personal Contact: Personal Mobile'] != "":
                    area = row['Personal Contact: Personal Mobile'][1:4]
                    phon = row['Personal Contact: Personal Mobile'][6:14]
                    print(workerid + ','
                          + "Personal Mobile" + ','
                          + cntry + ',' + intlcode + ',' + area + ',' + phon
                          + ',' + 'Phone Extension' + ',' + 'Public')

                if row['Work Contact: Work Phone'] != "":
                    area = row['Work Contact: Work Phone'][1:4]
                    phon = row['Work Contact: Work Phone'][6:14]
                    print(workerid + ','
                          + "Work Office" + ','
                          + cntry + ',' + intlcode + ',' + area + ',' + phon
                          + ',' + 'Phone Extension' + ',' + 'Public')

                if row['Work Contact: Work Mobile'] != "":
                    area = row['Work Contact: Work Mobile'][1:4]
                    phon = row['Work Contact: Work Mobile'][6:14]
                    print(workerid + ','
                          + "Work Mobile" + ','
                          + cntry + ',' + intlcode + ',' + area + ',' + phon
                          + ',' + 'Phone Extension' + ',' + 'Public')


            # except Exception as e:
            #     # print(repr(e))
            #     fn_write_error("Error in phone_rec.py Step 4, Error = "
            #                    + repr(e))
            #     fn_send_mail(settings.ADP_TO_EMAIL, settings.ADP_FROM_EMAIL,
            #              "Error in phone_rec.py, at reading diff file.  "
            #              "Error = " + repr(e),
            #              "Error in phone_rec.py")

        f.close()

    except Exception as e:
        print("Error in phone_rec.py, Error = " + repr(e))
        # fn_write_error("Error in phone_rec.py - Main: "
        #                + repr(e))
        # fn_send_mail(settings.ADP_TO_EMAIL, settings.ADP_FROM_EMAIL,
        #          "Error in phone_rec.py, Error = " + repr(e),
        #          "Error in phone_rec.py")

if __name__ == "__main__":
    main()
#     args = parser.parse_args()
#     test = args.test
#     database = args.database
#
# if not database:
#     print("mandatory option missing: database name\n")
#     exit(-1)
# else:
#     database = database.lower()
#
# if database != 'cars' and database != 'train' and database != 'sandbox':
#     print("database must be: 'cars' or 'train' or 'sandbox'\n")
#     parser.print_help()

sys.exit(main())
