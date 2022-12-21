############################################################################### 
# DATE: 20/12/2022

# AUTHOR: Marti Rovira

# AIM: Download information from a random selection of job openings using Reed 
# dot co dot uk API

# OUTPUT: CSV file called "Random_offers". If already exists, it concatenates 
# the offers to the old file.

# NOTE1: The execution of the file requires a .txt file in the Working Directory
# with the API password.

# NOTE2: This is the first code I share publicly. Please, feel free to reach me
# to suggest any improvements.
###############################################################################

# Setting libraries

#import numpy as np
import pandas as pd
import requests
import json
from getpass import getpass
from time import sleep
import random
import os
import datetime

# Setting path

path0 = os.getcwd()
os.chdir(path0)

# Setting passwords

api_reed_access = open(path0 + '/api_reed_password.txt', 'r')
api_reed_code = api_reed_access.read()
api_reed_access.close() 

# Setting date and time ()

today = datetime.date.today()
datetoday = today.strftime("%d/%m/%Y")
#datetoday2 = today.strftime("%Y_%m_%d")

now=datetime.datetime.now()
time = now.strftime("%H:%M:%S")
#time2 = now.strftime("%H_%M_%S")

#Detecting the total number of offers available at Reed.co.uk.
url = 'https://www.reed.co.uk/api/1.0/search?'
JSONContent = requests.get(url, auth=(api_reed_code,""), timeout=60).json()

totalresultsREED = JSONContent['totalResults']

# Getting a random sample of 1000 jobs each day

# Calculating the range
n = random.randint(0,JSONContent['totalResults']-1000)
totalresultsREED2=n+1000

JSONContent_fulldb = []
for i in range(n, totalresultsREED2, 100):
    url = url +'&resultstoSkip='+str(i)
    JSONContent = requests.get(url, auth=(api_reed_code,""), timeout=10).json()
    JSONContent_fulldb.append(JSONContent)
    sleep(2)
    content = json.dumps(JSONContent_fulldb, indent = 4, sort_keys=True)

if totalresultsREED2 % 100 == 0:
    range_out = (totalresultsREED2/100)
else:
    range_out = (totalresultsREED2/100)+1

# Creating the database
random_offers_today = pd.DataFrame(columns=['Jobid', 
                                             'employerId',
                                             'employerName',
                                             'Job',
                                             'Location',
                                             'Date',
                                             'ExpirationDate',
                                             'Description',
                                             'Minsalary',
                                             'Maxsalary',
                                             'currency',
                                             'applications'])

# Scrapping 100 offers at a time (max allowed by API) and 
# concatenating with general database.

for j in range(0,10):
    location_list = []
    json1_data = json.loads(content)[j]
    for var in json1_data['results']:
        location_list.append([var['jobId'], 
                              var['employerId'], 
                              var['employerName'],
                              var['jobTitle'], 
                              var['locationName'], 
                              var['date'], 
                              var['expirationDate'], 
                              var['jobDescription'], 
                              var['minimumSalary'], 
                              var['maximumSalary'], 
                              var['currency'], 
                              var['applications']])
        
    df = pd.DataFrame(location_list)
    df.columns = ['Jobid', 
                       'employerId',
                       'employerName',
                       'Job',
                       'Location',
                       'Date',
                       'ExpirationDate',
                       'Description',
                       'Minsalary',
                       'Maxsalary',
                       'currency',
                       'applications']
    random_offers_today = pd.concat([random_offers_today, df], sort=False)
    random_offers_today['first_seen_date']=datetoday
    random_offers_today['first_seen_time']=time

# Saving the file

namefile = path0 + "/Random_offers.csv"
isFile = os.path.isfile(namefile)

if isFile == True:
    prev_jobs = pd.read_csv(namefile, sep=';')
    combined_csv = pd.concat([prev_jobs, random_offers_today])
    combined_csv.to_csv(namefile, index=False, encoding='utf-8-sig', sep=";")
else:
    random_offers_today.to_csv(namefile, sep=";")

print(datetoday + ": Random scrap of job offers finnished")