#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 13:19:15 2021

@author: mam
"""

# before starting this program, run this in your shel
# read -s -p "Enter password for felix:" FELIXPASS && export FELIXPASS
import os
import psycopg2
import pandas as pds

# Get environment variables
FELIXPASS = os.getenv('FELIXPASS')

# print(FELIXPASS)

con = psycopg2.connect(
    host="localhost",
    database="felix",
    user="mam",
    password=FELIXPASS, 
    port = "1111")

cur = con.cursor()

cols_in_table_q = """
SELECT column_name
  FROM information_schema.columns
 WHERE table_schema = 'public'
   AND table_name   = 'modifications'
"""

cur.execute(cols_in_table_q)
felix_modifications_model = cur.fetchall()
felix_modifications_cols = pds.DataFrame(felix_modifications_model)
felix_modifications_cols = felix_modifications_cols.iloc[:,0].to_list()

cur.execute("SELECT * from modifications")
rows = cur.fetchall()
cur.close()
con.close()
felixframe = pds.DataFrame(rows, columns=felix_modifications_cols)

felixframe.to_csv('data/felix_modifications.tsv', sep='\t')
