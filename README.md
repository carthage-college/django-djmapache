# django-djmapache
Middleware applications that provide the data transfer between third party
SAAS entities and internal databases.

# security onion for packetfence

so-master.carthage.edu

/etc/elastalert/rules/
/data2/python_venv/3.5/packetfence/

the code in the packetfence directory is not in git,
which we cannot use on that server, so we store code here.

# crontab for larry
# handshake
00 03 * * * (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/handshake/buildcsv.py --database=cars 2>&1 | mail -s "[DJ Mapache] Handshake CSV generator" larry@carthage.edu) >> /dev/null 2>&1
# JX scripts
11 11 * * * (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/class_year.py --action=update --database=jxlive 2>&1 | mail -s "[DJ Mapache] Class Year" larry@carthage.edu) >> /dev/null 2>&1
# scrip safe
33 * * * * (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/scrip_safe.py --test 2>&1 | mail -s "[scrip safe] SFTP process" larry@carthage.edu) >> /dev/null 2>&1
# OCLC: weekly, monday morning at 2h, push out a fresh copy of the OCLC xml
00 02 * * 1 (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/oclc.py 2>&1 | mail -s "[OCLC] FTP carthage user data" larry@carthage.edu) >> /dev/null 2>&1
# Terra Dotta: daily before 2h CDT, push out a copy of the Terra Dotta export
30 01 * * * (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/terradotta.py 2>&1 | mail -s "[TerraDotta] SFTP carthage user data" larry@carthage.edu) >> /dev/null 2>&1

# DJ Mapache
<img src="https://raw.githubusercontent.com/carthage-college/django-djmapache/master/djmapache/static/img/mapache.png" alt="mapache" height="400" width="600">
