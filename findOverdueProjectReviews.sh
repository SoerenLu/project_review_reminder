#!/bin/bash

#   script to download (wget) and parse (parseProjectlist.py) the projectlist (https://ispe-qm.fzi.de/wiki/IDS-TKS-QM-Projektliste) of IDS to find projects with overdue projectreviews and prewrite mails to file which then have to be sent manually.

#load your password for https://ispe-qm.fzi.de/login
source config

#create the folder in which the mails are going to be written
mkdir -p mails/$(date '+%Y-%b-%d')

#login to https://ispe-qm.fzi.de/login
wget --no-check-certificate --user langhors --password "$password" --save-cookies=cookies --keep-session-cookies https://ispe-qm.fzi.de/login

#download the whole projectlist-website
wget --no-check-certificate --load-cookies=cookies https://ispe-qm.fzi.de/wiki/IDS-TKS-QM-Projektliste

#read downloaded projectlist-website and write mails to textfiles
python parseProjectlist.py

#delete the downloaded website and other files that we dont need anymore
rm IDS-TKS-QM-Projektliste login cookies
