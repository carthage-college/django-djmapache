# -*- coding: utf-8 -*-

import os, sys
import requests

# shell environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.shell')

from django.conf import settings

from djmapache.packetfence.utils import get_token

API_EARL = settings.PACKETFENCE_API_EARL


def main():
    """Display the number of nodes."""
    token = get_token()
    print(token)
    headers = dict(
        accept='application/json', Authorization=token
    )
    url = '{}{}/active'.format(API_EARL, settings.PACKETFENCE_REPORTS_ENDPOINT)
    resp = requests.get(url=url, headers=headers, verify=False)
    data = resp.json()
    for c, item in enumerate(data['items']):
        print(c,item)
    print(len(data['items']))


if __name__ == "__main__":

    sys.exit(main())
