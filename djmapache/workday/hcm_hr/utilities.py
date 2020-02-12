import csv

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


def fn_write_phone_cl(file, data):
    with open(file, 'a') as phone_output:
        csvwriter = csv.writer(phone_output)
        csvwriter.writerow(data)

def fn_write_email_cl_header(file):
    with open(file, 'w') as email_output:
        csvwriter = csv.writer(email_output)
        csvwriter.writerow(["Worker ID", "Email Type", "Email Address",
                            "Public"])

def fn_write_email_cl(file, data):
    with open(file, 'a') as email_output:
        csvwriter = csv.writer(email_output)
        csvwriter.writerow(data)