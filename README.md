# django-djmapache
Middleware applications that provide the data transfer between third party
SAAS entities and internal databases.

# crontab for larry
# handshake
00 03 * * * (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/handshake/buildcsv.py --database=cars 2>&1 | mail -s "[DJ Mapache] Handshake CSV generator" larry@carthage.edu) >> /dev/null 2>&1
