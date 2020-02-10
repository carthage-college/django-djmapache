#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
import requests

from settings.local import API_EARL
from settings.local import REPORTS_ENDPOINT
from utils.helpers import get_token


def main():
    """Display the number of nodes."""
    token = get_token()
    print(token)
    headers = dict(
        accept='application/json', Authorization=token
    )
    url = '{}{}/active'.format(API_EARL, REPORTS_ENDPOINT)
    resp = requests.get(url=url, headers=headers, verify=False)
    data = resp.json()
    for c, item in enumerate(data['items']):
        print(c,item)
    print(len(data['items']))


if __name__ == "__main__":

    sys.exit(main())
