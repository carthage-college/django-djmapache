# -*- coding: utf-8 -*-

import os, sys
import requests
import json

# shell environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.shell')

from django.conf import settings

API_EARL = settings.PACKETFENCE_API_EARL


def get_token():
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = dict(
        username=settings.PACKETFENCE_USERNAME,
        password=settings.PACKETFENCE_PASSWORD
    )
    url = API_EARL + settings.PACKETFENCE_LOGIN_ENDPOINT
    resp = requests.post(url=url, data=json.dumps(params), headers=headers, verify=False)
    return json.loads(resp.content)['token']


def main():
    """
    display the number of nodes
    """
    token = get_token()
    print(token)
    headers = dict(
        accept='application/json', Authorization=token
    )
    url = '{}{}/active'.format(API_EARL, settings.PACKETFENCE_REPORTS_ENDPOINT)
    resp = requests.get(url=url, headers=headers, verify=False)
    data = resp.json()
    print(len(data['items']))


######################
# shell command line
######################

if __name__ == "__main__":

    sys.exit(main())
