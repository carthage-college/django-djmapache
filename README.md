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
# Papercut: monthly, 2nd day of every month at 23:55h, create .csv file for Papercut charge backs
55 23 2 * * (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/papercut.py 2>&1 | mail -s "[PaperCut] Papercut charge backs data" larry@carthage.edu) >> /dev/null 2>&1
## Papercut GL: monthly, 3rd day of every month at 2:45h, create .csv file of Papercut GL accounts
#45 02 3 * * (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/papercut_glrec.py 2>&1 | mail -s "[PaperCut] Papercut GL accounts data" larry@carthage.edu) >> /dev/null 2>&1
# scrip safe
33 * * * * (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/scrip_safe.py --test 2>&1 | mail -s "[scrip safe] SFTP process" larry@carthage.edu) >> /dev/null 2>&1
# Everbridge: weekly, monday morning at midnight
00 00 * * 1 (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/everbridge.py --database=cars 2>&1 | mail -s "[Everbridge] SFTP carthage user data" larry@carthage.edu) >> /dev/null 2>&1
# OCLC: weekly, monday morning at 2h, push out a fresh copy of the OCLC xml
00 02 * * 1 (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/oclc.py 2>&1 | mail -s "[OCLC] FTP carthage user data" larry@carthage.edu) >> /dev/null 2>&1
# maxient
#00 08 * * * (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/maxient.py) >> /dev/null 2>&1
00 10 * * * (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/maxient.py 2>&1 | mail -s "[Maxient] SFTP carthage user data" larry@carthage.edu) >> /dev/null 2>&1
# barnes and noble
18 08-18 * * 1-6 (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/barnesandnoble.py) >> /dev/null 2>&1
30 00 * * * (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/barnesandnoble_crs_enr.py) >> /dev/null 2>&1
# testing only
#18 08-18 * * 1-6 (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/barnesandnoble.py 2>&1 | mail -s "[Barnes & Noble] SFTP carthage user data" larry@carthage.edu) >> /dev/null 2>&1
# package concierge
00 03 * * MON (cd /data2/python_venv/3.6/djmapache/ && . bin/activate && bin/python djmapache/bin/concierge.py --database=cars 2>&1 | mail -s "[Package Concierge] SFTP carthage data" larry@carthage.edu) >> /dev/null 2>&1

# DJ Mapache
<img src="https://raw.githubusercontent.com/carthage-college/django-djmapache/master/djmapache/static/img/mapache.png" alt="mapache" height="400" width="600">
