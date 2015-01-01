#!/usr/bin/python

import time
import psycopg2 as db
import os, sys, subprocess as sub
path = '/fahstats/scripts/python'
if path not in sys.path:
   sys.path.append(path)
from setup import connStr

try:
   db.connect(connStr['teste'])
except:
   os.system('service pgpool stop')
   time.sleep(5)
   os.system('service pgpool start')
   raise
