# -*- coding: utf-8 -*-
"""
Created on Sun Nov  7 18:16:12 2021

@author: BlueSpark
"""
import sqlite3 as db
import pandas as pd
import json
from sqlalchemy import create_engine

inputfile='css-scraper-results.json'
df=pd.DataFrame(json.load(open(inputfile)))
df["tags"]=pd.Series([",".join(each) for each in df["tags"]])
engine = create_engine("sqlite://")
con= db.connect('scrape-css.db')
df.to_sql("quotes", con,chunksize=1000)