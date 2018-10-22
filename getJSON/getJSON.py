##########################################################################################
##########################################################################################
####
####
####    Author:           Henry Steele, Library Technology Services, Tufts University
####    Name of Program:  publishNotes.py
####    Date created:     2017-09
####
####    Purpose:
####    Use the ArchivesSpace API to iterate over the set or subset of
####    records records in ArchivesSpace and update each of
####    their notes, and each subnote on the scope-content note, so that
####    they will publish and display in resource record exports from ArchiveSpace.
####
####
####	The script prompts the user for inputs on instance (dev1, dev2, or prod),
####	the type of note they want to publish (e.g. "scopecontent"), and the type of
####	record they want to run the update on.
####
####	It also prompts the user for an input file of record numbers.  It is expecting
####	a list of IDs from a MySQL report on records of that type Publish values of "False"
####	for that record type.  This is to improve the performance of the program, especially
####	for archival and digital objecs, for which there are 100,000s of records.
####
####
####    Inputs:  		A list of resource, archival object, and/or digital object ids
####					exported from MySQL.  (Make sure you are exporting these reports
####					from the right instance!)
####
####    Environment:	Python >= v 3.6
####    				sys, os, json, requests, Tkinter::Tk modules
####
####    Output:
####    	- updated ArchivesSpace resource records
####    	- 'Multi-part Note Log.txt'
####   			+ contains a log entry for each resource, whether it had a
####              scope-content note,
####   			  and whether the note and its subnote could be updated.
####   		- 'Counts for Log.txt'
####   			+ counts of how many resources were updated, how many had notes,
####   			+ and how many update errors there were (for the update script).
####
##########################################################################################
##########################################################################################

import sys

import requests
import json
import os
import time
import csv
from Tkinter import Tk
from tkFileDialog import askopenfilename
sys.path.append('scripts/')
from functions import *
sys.path.append('secrets/')
import secrets



##############
############## You need to pip install the "sys", "os", "requests" and "json," python modules.  You don't need to install Tkinter because
############## this is included with a standard Python installation

#create directory for log output

## Get parameters from user

print "\n\n"
print "#############################################################################"
print "#############################################################################"
print "#######"
print "#######    This program gets JSON records for a user-defined record type."
print "#######    You specify the type of note, the instance of ASpace, "
print "#######    and the record type."
print "#######"
print "#############################################################################"
print "#############################################################################"
# noteTypeInteger = raw_input("\n\nWhat type of note do you want to publish?: \n\n      1) 'scopecontent' notes\n      2) 'prefercite' notes\n\nSelect an option: ")

# noteType = ""
# if noteTypeInteger == "1":
	# noteType = "scopecontent"
# elif noteTypeInteger == "2":
	# noteType = "prefercite"


# print ("\nNote type: " + noteType)

instanceInputInteger = raw_input("\n\nWhat instance to you want to retrieve records for?\n\n      1) dev-01\n      2) dev-02\n      3) prod\n\nSelect an option: ")

if instanceInputInteger == "1":
	instance = "dev-01"

elif instanceInputInteger == "2":
	instance = "dev-02"

elif instanceInputInteger == "3":
	instance = "prod"

print ("\nInstance: " + str(instance))

if instanceInputInteger != "1" and instanceInputInteger != "2" and instanceInputInteger != "3":
	print "\nUnknown instance.  Try again."
	quit()

resourceBool = raw_input("\n\nDo you want JSON for RESOURCE records? (y or n): ")
resourceBoolFull = ""
AOBool = raw_input("Do you want JSON for ARCHIVAL OBJECT records? (y or n): ")
AOBoolFull = ""
DOBool = raw_input("Do you want JSON for DIGITAL OBJECT records? (y or n): ")
DOBoolFull = ""

if resourceBool != "y" and resourceBool != "Y" and resourceBool != "yes" and resourceBool != "Yes" and resourceBool != "n" and resourceBool != "N" and resourceBool != "no" and resourceBool != "No":
	print "\n\nUnknown answer.  Try again."
	quit()

if AOBool != "y" and AOBool != "Y" and AOBool != "yes" and AOBool != "Yes" and AOBool != "n" and AOBool != "N" and AOBool != "no" and AOBool != "No":
	print "\n\nUnknown answer.  Try again."
	quit()

if DOBool != "y" and DOBool != "Y" and DOBool != "yes" and DOBool != "Yes" and DOBool != "n" and DOBool != "N" and DOBool != "no" and DOBool != "No":
	print "\n\nUnknown answer.  Try again."
	quit()


if resourceBool == "y" or resourceBool == "Y" or resourceBool == "yes" or resourceBool == "Yes":
	resourceBoolFull = "yes"
else:
	resourceBoolFull = "no"

if AOBool == "y" or AOBool == "Y" or AOBool == "yes" or AOBool == "Yes":
	AOBoolFull = "yes"
else:
	AOBoolFull = "no"

if DOBool == "y" or DOBool == "Y" or DOBool == "yes" or DOBool == "Yes":
	DOBoolFull = "yes"
else:
	DOBoolFull = "no"

print("\n\nRecord types to change:\n      \nResource? " + resourceBoolFull + "      \nAO?       " + AOBoolFull + "      \nDO?       " + DOBoolFull)

#time.sleep(2)

url = ""
hostname = ""

if instanceInputInteger == "1":
	hostname =  secrets.dev_host
	url = secrets.dev_host + "/users/" + secrets.dev_username + "/login?password=" + secrets.dev_password
elif instanceInputInteger == "2":
	hostname = "http://as2.library.tufts.edu:8092"
	url = "http://as2.library.tufts.edu:8092/users/admin/login?password=admin"
elif instanceInputInteger == "3":
	hostname = secrets.prod_host
	url = secrets.prod_host + "/users/" + secrets.prod_username + "/login?password=" + secrets.prod_password

#print ("\n\nURL for login:               " + url)
#print ("\nHostname for accessing records:  " + hostname + "\n\n")





#get filename from GUI file picker
Tk().withdraw()

resourceListCounter = 0
AOListCounter = 0
DOListCounter = 0

if resourceBool != "n" and resourceBool != "N" and resourceBool != "no" and resourceBool != "No":

	filenameResource = askopenfilename(title = "Select RESOURCE IDs input file")

	print(filenameResource)

	resourceList = []

	with open(filenameResource, 'rb') as file1:
		for line in file1:
			resourceList.append(line)
			resourceListCounter = resourceListCounter + 1

	print "\n\nNumber of resource records in file:                 " + str(resourceListCounter)

if AOBool != "n" and AOBool != "N" and AOBool != "no" and AOBool != "No":
	filenameAO = askopenfilename(title = "Select ARCHIVAL OBJECT IDs input file")

	print(filenameAO)

	AOList = []

	with open(filenameAO, 'rb') as file2:
		for line in file2:
			AOList.append(line)
			AOListCounter = AOListCounter + 1

	print "\n\nNumber of archival object records in file: " + str(AOListCounter)

if DOBool != "n" and DOBool != "N" and DOBool != "no" and DOBool != "No":
	filenameDO = askopenfilename(title = "Select DIGITAL OBJECT IDs input file")

	print(filenameDO)

	DOList = []

	with open(filenameDO, 'rb') as file3:
		for line in file3:
			DOList.append(line)
			DOListCounter = DOListCounter + 1

	print "\n\nNumber of digital objects records in file: " + str(DOListCounter)

#create directory for log output
oDir = "./Output"
if not os.path.isdir(oDir) or not os.path.exists(oDir):
	os.makedirs(oDir)



## establish API session
try:
	auth = requests.post(url).json()

except requests.exceptions.RequestException as e:
	print ("\n\nInvalid URL, try again")
	exit()

	##test authentication

if auth.get("session") == None:
	print ("\n\nWrong username or password! Try Again")
	exit()

else:
	print ("\n\nHello " + auth["user"]["name"])

session = auth["session"]

headers = {'X-ArchivesSpace-Session':session}

type_label = ""

resourceType = "resource"
AOType = "archival_object"
DOType = "digital_object"

#print("DO Type: " + DOType)

if resourceBool != "n" and resourceBool != "N" and resourceBool != "no" and resourceBool != "No":
	returnJSON(resourceList, headers, resourceType, hostname)

if AOBool != "n" and AOBool != "N" and AOBool != "no" and AOBool != "No":
	returnJSON(AOList, headers, AOType, hostname)

if DOBool != "n" and DOBool != "N" and DOBool != "no" and DOBool != "No":
	returnJSON(DOList, headers, DOType, hostname)
