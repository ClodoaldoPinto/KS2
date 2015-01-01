# -*- coding: utf-8 -*-
import os.path

conn_string = "host=%s port=%s dbname=%s user=%s password=%s" % (
    "localhost", "5432", "folding", "phpUser", "somepassword")
row_count = 200
home_path = '/home/kakaostats.com'
templates_path = os.path.join(home_path, 'templates')
