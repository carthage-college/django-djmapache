# django-djmapache
Middleware applications that provide the data transfer between third party
SAAS entities and internal databases.

# crontab for larry
# handshake
00 03 * * * (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/handshake/buildcsv.py --database=cars 2>&1 | mail -s "[DJ Mapache] Handshake CSV generator" larry@carthage.edu) >> /dev/null 2>&1
# JX scripts
11 11 * * * (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/class_year.py --action=update --database=jxlive 2>&1 | mail -s "[DJ Mapache] Class Year" larry@carthage.edu) >> /dev/null 2>&1

# Mapache
<img src="https://raw.githubusercontent.com/carthage-college/django-djmapache/master/djmapache/static/img/mapache.png" alt="mapache" height="400" width="600">
