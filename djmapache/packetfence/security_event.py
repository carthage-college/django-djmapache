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
Accepts as input a MAC address and sets a security event on it in PacketFence.
"""

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    '-a', '--action',
    required=True,
    help="Security action e.g. apply_security_event",
    dest='action'
)
parser.add_argument(
    '-i', '--sid',
    required=True,
    help="Security event ID e.g. 2000000",
    dest='sid'
)
parser.add_argument(
    '-m', '--mac',
    required=True,
    help="MAC address",
    dest='mac'
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test'
)


def main():
    """Trigger a security event on a MAC address."""
    token = get_token()
    if test:
        print(token)

    headers = dict(
        accept='application/json', Authorization=token
    )
    if test:
        print(headers)

    data = '{{"security_event_id": "{0}", "mac": "{1}"}}'.format(sid, mac)
    if test:
        print(data)
    url = '{0}{1}/{2}/{3}'.format(
        API_EARL, settings.PACKETFENCE_NODE_ENDPOINT, mac, action,
    )
    if test:
        print(url)
    resp = requests.post(url=url, headers=headers, data=data, verify=False)
    data = resp.json()
    if test:
        print(data)

    for count, item in enumerate(data):
        print(count,item,data[item])


if __name__ == "__main__":
    args = parser.parse_args()
    mac = args.mac
    sid = args.sid
    action = args.action
    test = args.test

    if test:
        print(args)


    sys.exit(main())
