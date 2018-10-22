def getJSON(recordID, head, host_name, apiType):


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
		line1 = str(record_id) + "~~" + term + "~~~~NO NOTES OF TYPE " + nT.upper() + "\n"
		print(line1)
		f.write(line1)
		
	return(listOfLists, typeNotesBool)

	
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
	
	#pList is all the notes of the desired type on the resource
	if len(pList) == 0:
		lineB = str(record_id) + "~~" + term + "~~~~NO " + nT.upper() + " NOTES\n"
		print(lineB)
		f.write(lineB)
		
	y = 0
	
	# element is each scopecontent note on the resource
	for element in pList:
	
		fC.write(str(element) + "\n")
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
					lineB = str(record_id) + "~" + term + "~" + str(note_id) + "~" + str(noteBool) + "~" + "Subnote number - " + str(y - 2 + 1) + "~" +  str(element3) + "~\n"
					print(lineB)
					f.write(lineB)
			y = y + 1
			
		#x = x + 1

	if y == 0:
		lineB = str(record_id) + "~~" + term + "~~~~NO " + nT.upper() + " NOTES\n"
		print(lineB)
		f.write(lineB)
		
	print ("\n\n")