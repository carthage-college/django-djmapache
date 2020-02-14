import csv
from djimix.core.utils import get_connection, xsql


def fn_format_country(cntry_code):
    if cntry_code == "USA":
        cntry = 'United States of America'
    elif cntry_code == "CAN":
        cntry = 'Canada'
    elif cntry_code == "CHN":
        cntry = 'China'
    elif cntry_code == "DEU":
        cntry = 'German'
    elif cntry_code == "SRB":
        cntry = 'Serbia'
    else:
        cntry = "Country Unavailable"

    return cntry

def fn_format_cx_country(cntry_code):
    if cntry_code == "CDN":
        cntry = 'Canada'
    elif cntry_code == "B":
        cntry = 'Belgium'
    elif  cntry_code == "USA":
        cntry = 'United States of America'
    elif cntry_code == "CHI":
        cntry = 'China'
    elif cntry_code == "CN":
        cntry = 'China'
    elif cntry_code == "I":
        cntry = 'Italy'
    elif cntry_code == "J":
        cntry = 'Japan'
    elif cntry_code == "EAK":
        cntry = 'Kenya'
    elif cntry_code == "KE":
        cntry = 'Kenya'
    elif cntry_code == "GER":
        cntry = 'Germany'
    elif cntry_code == "RA":
        cntry = 'Argentina'
    elif cntry_code == "SS":
        cntry = 'Serbia'
    elif cntry_code == "RFC":
        cntry = 'Cameroon'
    elif cntry_code == "SN":
        cntry = 'Senegal'
    else:
        cntry = "Country Unavailable"

    return cntry


def fn_format_phone(cntry_code, phone):
    if cntry_code == "USA":
        intlcode = '1'
        area = phone[1:4]
        phon = phone[6:14]
    elif cntry_code == "CAN":
        intlcode = '1'
        area = phone[1:4]
        phon = phone[6:14]
    # elif cntry_code == "CHN":
    #     cntry = 'China'
    # elif cntry_code == "DEU":
    #     cntry = 'German'
    # elif cntry_code == "SRB":
    #     cntry = 'Serbia'
    else:
        intlcode = '1'
        area = phone[1:4]
        phon = phone[6:14]

    return intlcode, area, phon

def fn_write_phone_cl_header(file):
    with open(file, 'w') as phone_output:
        csvwriter = csv.writer(phone_output)
        csvwriter.writerow(["Worker ID", "Phone Type", "Country (Phone)",
                            "International Phone Code", "Area Code",
                            "Phone Number", "Phone Extension", "Public"])


def fn_write_email_cl_header(file):
    with open(file, 'w') as email_output:
        csvwriter = csv.writer(email_output)
        csvwriter.writerow(["Worker ID", "Email Type", "Email Address",
                            "Public"])

def fn_write_addr_cl_header(file):
    with open(file, 'w') as addr_output:
        csvwriter = csv.writer(addr_output)
        csvwriter.writerow(["Worker ID", "Country", "Address Type",
                            "Address Usage", "Region", "Subregion", "City",
                            "City Subdivision","Postal Code", "Address Line 1",
                            "Address Line 2", "Address Line 3",
                            "Address Line 4", "Remote EE"])

# def fn_write_addr_cl(file, data):
#     with open(file, 'a') as addr_output:
#         csvwriter = csv.writer(addr_output)
#         csvwriter.writerow(data)

def fn_write_name_cl_header(file):
    with open(file, 'w') as name_output:
        csvwriter = csv.writer(name_output)
        csvwriter.writerow(["Worker ID", "Worker Type", "First Name",
                            "Middle Name", "Last Name", "Legal Name Country",
                            "Title", "Family Name Prefix", "Suffix",
                            "Preferred First Name",
                            "Preferred Middle Name", "Preferred Last Name",
                            "Local Script First Name",
                            "Local Script Last Name"])


def fn_write_personal_cl_header(file):
    with open(file, 'w') as name_output:
        csvwriter = csv.writer(name_output)
        csvwriter.writerow(["Worker ID", "Date of Birth", "Date of Death",
                            "Gender", "Personal Data Country", "Marital Status",
                            "Marital Status Date"])

def fn_write_clean_file(file, data):
    with open(file, 'a') as output:
        csvwriter = csv.writer(output)
        csvwriter.writerow(data)


def fn_get_id(adp_id, EARL, DEBUG):
    try:
        connection = get_connection(EARL)
        # connection closes when exiting the 'with' block
        QUERY = '''select cx_id_char 
            from cvid_rec where adp_id = {0}'''.format(adp_id)

        with connection:
            data_result = xsql(
                QUERY, connection, key=DEBUG
            ).fetchone()
            return data_result[0].strip()
            # print(data_result[0])
            # ret = data_result[0]
            # print("Carthage id is: " + ret)

    except Exception as e:
        print("Error in utilities.py fn_get_id , Error = " + repr(e))
        # fn_write_error("Error in email_rec.py - fn_get_id: "
        #                + repr(e))
        # fn_send_mail(settings.ADP_TO_EMAIL, settings.ADP_FROM_EMAIL,
        #          "Error in utilities.py fn_get_id, Error = " + repr(e),
        #          "Error in utilities.py fn_get_id")