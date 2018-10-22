import requests
import json
import os
def getJSON(recordID, head, host_name, apiType):

	print("\n" + host_name + "/repositories/2/" + apiType + "/" + str(recordID) + "\n")
	try:
		json_object = requests.get(host_name + "/repositories/2/" + apiType + "/" + str(recordID), headers=head).json()

	except:
		print ("Couldn't retrieve JSON representation of record")
		jsonObject = ""

	return json_object

def postJSON(recordID, o, head, host_name, apiType):

	resource_data = json.dumps(o)
	success = ""

	try:
		postResult = requests.post(host_name + "/repositories/2/" + apiType + "/" + str(recordID), headers=head, data=resource_data).json()
		success = "Pass"
	except:
		print "Error posting updated resource " + str(recordID) + "\n"
		success = "Fail"



	return(success)


## creates and returns a 3D list for updating and printing
def getValues(n, record_id, f, term, nT):

	#master list
	listOfLists = []

	y = 0

	typeNotesBool = False


	for note in n:
		#a list for each scopecontent note
		publishList = []

		if note["type"] == nT:

			y = y + 1
			#a sublist for each subnote
			subList = []
			publishList.append(note["persistent_id"])
			publishList.append(note["publish"])
			z = 0
			for subNote in note["subnotes"]:
				subList.append(subNote["publish"])
				z = z + 1

			if z == 0:
				subList = ["N/A"]
				publishList.append(subList)

			publishList.append(subList)

			listOfLists.append(publishList)
	if y > 0:
		typeNotesBool = True

	if y == 0:
		typeNotesBool = False
		record_id = str(record_id)
		record_id = record_id.strip()
		line1 = record_id + "~~" + term + "~~~~NO NOTES OF TYPE " + nT.upper() + "\n"
		print(line1)
		f.write(line1)

	return [listOfLists, typeNotesBool]


def updateValues(o, nT):
	x = 0
	for note in o["notes"]:

		y = 0
		if note["type"] == nT:
			o["notes"][x]["publish"] = True

			for subNote in note["subnotes"]:
				o["notes"][x]["subnotes"][y]["publish"] = True
				y = y + 1

		x = x + 1

	return o



def printNotes(term, pList, f, record_id, nT):

	lineB = ""

	#pList is all the notes of the desired type on the resource
	if len(pList) == 0:
		record_id = str(record_id)
		record_id = record_id.strip()
		lineB = record_id + "~~" + term + "~~~~NO " + nT.upper() + " NOTES\n"
		print(lineB)
		f.write(lineB)

	y = 0

	# element is each scopecontent note on the resource
	for element in pList:

		#fC.write(str(element) + "\n")
		note_id = ""
		noteBool = False

		# element2 is each part of the scope-content list, including the scope-content note's ID hash, publish value, and an array of
		# all the subnotes' publish values.

		# the id of the subnote is simply a counter value in this script
		for element2 in element:

			if y == 0:
				note_id = element[0]

			elif y == 1:
				noteBool = element[1]

			elif y == 2:

				for element3 in element2:
					noteTextID = y
					record_id = str(record_id)
					record_id = record_id.strip()
					lineB = record_id + "~" + term + "~" + str(note_id) + "~" + str(noteBool) + "~" + "Subnote number - " + str(y - 2 + 1) + "~" +  str(element3) + "\n"
					print(lineB)
					f.write(lineB)
			y = y + 1

		#x = x + 1

	if y == 0:
		record_id = str(record_id)
		record_id = record_id.strip()
		lineB = record_id + "~~" + term + "~~~~NO " + nT.upper() + " NOTES\n"

	#print(lineB)
	#f.write(lineB)

	print ("\n\n")

def publish(list, h, typeLabel, host, note_t):
	oDir = "./Output"
	if not os.path.isdir(oDir) or not os.path.exists(oDir):
		os.makedirs(oDir)

	fout = open(oDir + "/Multi-Part Note Log.txt", "wt")
	foutCounts = open(oDir + "/Counts for Log.txt", "wt")

	fout.write("ID~State~Note ID~Note Publish?~Note Text Number~Note Text Publish?~Notes\n")

	count = 0
	notesRetrieveCount = 0
	fail = 0

	typeLabelUpper = typeLabel
	typeLabelUpper.upper()

	api_type = ""

	if typeLabel == "resource":
		api_type = "resources"
	elif typeLabel == "archival_object":
		api_type = "archival_objects"
	elif typeLabel == "digital object":
		api_type = "digital_objects"

	if len(list) == 0:
		print("Your " + typeLabel + " list is empty.\n\n")

	else:
		for recordNumber in list:

			count = count + 1

			recordNumberString = str(recordNumber)
			recordNumberString = recordNumberString.strip('\r\n')

			try:
				jsonObject = getJSON(recordNumberString, h, host, api_type)

			except:
				#print("~~~~~~COULD NOT RETRIEVE RECORD ID: " + str(recordNumber) + "\n")
				fout.write("~~~~~~COULD NOT RETRIEVE RECORD ID: " + recordNumberString)
				fail = fail + 1
				continue

			if "notes" not in jsonObject or len(jsonObject["notes"]) == 0 or jsonObject["notes"] == "":
				print("~~~~~~NO NOTES SECTION FOR RECORD ID: " + recordNumberString)
				fout.write("~~~~~~NO NOTES SECTION FOR RECORD ID: " + recordNumberString)
				fail = fail + 1
				continue

			else:
				notes = jsonObject["notes"]
				notesRetrieveCount = notesRetrieveCount + 1
				#print notes
			try:
				returnArray = getValues(notes, recordNumber, fout, "Original State", note_t)


			except:
				print("COULD NOT RETRIEVE NOTES FOR RECORD ID: " + recordNumberString)
				fout.write("~~~~~~COULD NOT RETRIEVE NOTES FOR RECORD ID: " + recordNumberString)
				fail = fail + 1
				continue

			returnList = returnArray[0]
			tNB = returnArray[1]

			if tNB == False:
				continue

			## this is a 3D list containing a sublist for each scopecontent note on each resource,
			## and a sublist for each note text on each scopecontent note
			publishBegin = returnList

			##capture the initial state of publish settings and print them to the log
			#try:
			printNotes("Original state", publishBegin, fout, recordNumber, note_t)
			#except:
			#	print("~~~~~~PRINTING ERROR FOR RECORD ID: " + recordNumber + "\n")
			#	fout.write("~~~~~~~PRINTING ERROR FOR RECORD ID: " + recordNumber + "\n")
			#	fail = fail + 1
			#	continue

			jsonObject = updateValues(jsonObject, note_t)

			notes = jsonObject["notes"]

			success = postJSON(recordNumber, jsonObject, h, host, api_type)

			if success == "fail":
				print(str(recordNumber) + "~~~~~~COULDN'T UPDATE RECORD ID: " + recordNumberString + "\n")
				fout.write(str(recordNumber) + "~~~~~~COULDN'T UPDATE RECORD ID: " + recordNumberString + "\n")
				fail = fail + 1

			# get and print the end state of each resource's publish settings
			jsonObject = getJSON(recordNumber, h, host, api_type)


			notes = jsonObject["notes"]

			returnList2 = []
			publishEnd = []


			returnList2 = getValues(notes, recordNumber, fout, "Original State", note_t)

			publishEnd = returnList2[0]
			printNotes("Edited State", publishEnd, fout, recordNumber, note_t)

			## publish counts
	print("\n\n")
	fout.write("\n\n")


	print("Number of possible records in " + typeLabelUpper + " range: " + str(count) + "\n")
	foutCounts.write("Number of possible records in range: " + str(count) + "\n\n")

	print("Number of records in " + typeLabelUpper + " range with notes: " + str(notesRetrieveCount) + "\n")
	foutCounts.write("Number of records with notes: " + str(notesRetrieveCount) + "\n\n")


	print("Number of update failures. Check log: " + str(fail) + "\n")
	foutCounts.write("Number of update failures. Check log: " + str(fail) + "\n")

	print("\n\n\n\n")
	foutCounts.write("\n\n\n\n")


	fout.close
	foutCounts.close

def returnJSON(list, h, typeLabel, host):
	oDir = "./Output"
	if not os.path.isdir(oDir) or not os.path.exists(oDir):
		os.makedirs(oDir)

	fout = open(oDir + "/JSON Records.json", "wt")


	count = 0
	fail = 0

	typeLabelUpper = typeLabel
	typeLabelUpper = typeLabelUpper.upper()

	#print("Type Label: " + typeLabel)

	api_type = ""

	if typeLabel == "resource":
		api_type = "resources"
	elif typeLabel == "archival_object":
		api_type = "archival_objects"
	elif typeLabel == "digital_object":
		api_type = "digital_objects"

	#print("API Type: " + api_type)
	if len(list) == 0:
		print("Your " + typeLabel + " list is empty.\n\n")

	else:
		for recordNumber in list:

			count = count + 1

			recordNumberString = str(recordNumber)
			recordNumberString = recordNumberString.strip('\r\n')

			print("Record Number: " + recordNumberString)
			try:
				jsonObject = getJSON(recordNumberString, h, host, api_type)


			except:
				print("~~~~~~COULD NOT RETRIEVE RECORD ID: " + str(recordNumber) + "\n")
				#fout.write("~~~~~~COULD NOT RETRIEVE RECORD ID: " + recordNumberString)
				fail = fail + 1
				continue

			fout.write(json.dumps(jsonObject))
			# if "notes" not in jsonObject or len(jsonObject["notes"]) == 0 or jsonObject["notes"] == "":
				# print("~~~~~~NO NOTES SECTION FOR RECORD ID: " + recordNumberString)
				# fout.write("~~~~~~NO NOTES SECTION FOR RECORD ID: " + recordNumberString)
				# fail = fail + 1
				# continue

			# else:
				# notes = jsonObject["notes"]
				# notesRetrieveCount = notesRetrieveCount + 1
				# #print notes
			# try:
				# returnArray = getValues(notes, recordNumber, fout, "Original State", note_t)


			# except:
				# print("COULD NOT RETRIEVE NOTES FOR RECORD ID: " + recordNumberString)
				# fout.write("~~~~~~COULD NOT RETRIEVE NOTES FOR RECORD ID: " + recordNumberString)
				# fail = fail + 1
				# continue

			# returnList = returnArray[0]
			# tNB = returnArray[1]

			# if tNB == False:
				# continue

			# ## this is a 3D list containing a sublist for each scopecontent note on each resource,
			# ## and a sublist for each note text on each scopecontent note
			# publishBegin = returnList

			# ##capture the initial state of publish settings and print them to the log
			# #try:
			# printNotes("Original state", publishBegin, fout, recordNumber, note_t)
			# #except:
			# #	print("~~~~~~PRINTING ERROR FOR RECORD ID: " + recordNumber + "\n")
			# #	fout.write("~~~~~~~PRINTING ERROR FOR RECORD ID: " + recordNumber + "\n")
			# #	fail = fail + 1
			# #	continue

			# jsonObject = updateValues(jsonObject, note_t)

			# notes = jsonObject["notes"]

			# success = postJSON(recordNumber, jsonObject, h, host, api_type)

			# if success == "fail":
				# print(str(recordNumber) + "~~~~~~COULDN'T UPDATE RECORD ID: " + recordNumberString + "\n")
				# fout.write(str(recordNumber) + "~~~~~~COULDN'T UPDATE RECORD ID: " + recordNumberString + "\n")
				# fail = fail + 1

			# # get and print the end state of each resource's publish settings
			# jsonObject = getJSON(recordNumber, h, host, api_type)


			# notes = jsonObject["notes"]

			# returnList2 = []
			# publishEnd = []


			# returnList2 = getValues(notes, recordNumber, fout, "Original State", note_t)

			# publishEnd = returnList2[0]
			# printNotes("Edited State", publishEnd, fout, recordNumber, note_t)

			## publish counts
	print("\n\n")

	print("Number of possible records in " + typeLabelUpper + " range: " + str(count) + "\n")

	print("Number of update failures. Check log: " + str(fail) + "\n")

	print("\n\n\n\n")

	fout.close
