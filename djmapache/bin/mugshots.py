#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import sys

from django.conf import settings
from djimix.core.utils import get_connection
from djimix.core.utils import xsql


# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmapache.settings.shell')


def main():
    """Fetch mugshots from CMS."""
    root = settings.LIVEWHALE_API_URL
    connection = get_connection()
    sql = """
        SELECT
            *
        FROM
            provisioning_vw
        WHERE
            faculty IS NOT NULL OR staff IS NOT NULL
        ORDER BY
            lastname
    """
    with connection:
        users = xsql(sql, connection, key=settings.INFORMIX_DEBUG).fetchall()
    for user in users:
        earl = '{0}/live/json/profiles/search/{1}/'.format(root, user.username)
        response_search = requests.get(url=earl)
        json_search = response_search.json()
        if json_search:
            print(earl)
            email = '{0}@carthage.edu'.format(user.username)
            print('{0}'.format(email))
            for search in json_search:
                if isinstance(search.get('profiles_149'), list):
                    p149 = search.get('profiles_149')[0].strip()
                elif search.get('profiles_149'):
                    p149 = search.get('profiles_149').strip()
                else:
                    p149 = None
                status = (
                    (
                        search.get('profiles_37') and
                        search.get('profiles_37').strip() == email
                    ) or
                    (
                        p149 == email
                    ) or
                    (
                        search.get('profiles_80') and
                        search.get('profiles_80').strip() == email
                    ) or
                    (
                        search.get('profiles_45') and
                        search.get('profiles_45')[0].strip() == email
                    )
                )
                if status:
                    earl = '{0}/live/profiles/{1}@JSON'.format(root, search['id'])
                    print(earl)
                    response_profile = requests.get(url=earl)
                    profile = response_profile.json()
                    if profile.get('parent'):
                        earl = '{0}/live/profiles/{1}@JSON'.format(
                            root, profile['parent'],
                        )
                        print(earl)
                        response_parent = requests.get(url=earl)
                        profile = response_parent.json()
                    if profile.get('thumb'):
                        listz = profile['thumb'].split('/')
                        listz[8] = '300'
                        listz[0] = 'https:'
                        new_listz = listz[:9]
                        new_listz.append(listz[-1])
                        profile['thumbnail'] = '/'.join(new_listz)
                        # print(profile['thumbnail'])
                    local_phile = '/data2/www/data/profiles/{0}.jpg'.format(user.id)
                    thumb = profile.get('thumbnail')
                    if thumb:
                        print(local_phile)
                        with requests.get(thumb, stream=True) as request:
                            request.raise_for_status()
                            with open(local_phile, 'wb') as phile:
                                for chunk in request.iter_content(chunk_size=8192):
                                    phile.write(chunk)
                else:
                    print(search)


if __name__ == '__main__':
    sys.exit(main())
