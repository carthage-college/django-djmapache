# -*- coding: utf-8 -*-

import os, sys
import requests
import argparse

# shell environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.shell')

from django.conf import settings

from djmapache.packetfence.utils import get_token

API_EARL = settings.PACKETFENCE_API_EARL


# set up command-line options
desc = """
Accepts as input an IPv4 address
"""

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    '-i', '--ip',
    required=True,
    help="IPv4 address",
    dest='ip'
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test'
)


def main():
    """Obtain a mac address based on IPv4 address."""
    token = get_token()
    if test:
        print(token)

    headers = dict(
        accept='application/json', Authorization=token
    )
    if test:
        print(headers)
    url = '{0}{1}/ip2mac/{2}'.format(
        API_EARL, settings.PACKETFENCE_IP4LOGS_ENDPOINT, ip
    )
    if test:
        print(url)
    resp = requests.get(url=url, headers=headers, verify=False)
    data = resp.json()
    if test:
        print(data)

    for count, item in enumerate(data):
        print(count,item,data[item])


if __name__ == "__main__":
    args = parser.parse_args()
    ip = args.ip
    test = args.test

    if test:
        print(args)


    sys.exit(main())
