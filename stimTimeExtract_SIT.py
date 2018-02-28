# Author: Justin Wang

# running the script: python stimTimeExtract_JW.py {inputFileName} {OPTIONAL: outputDirectoryName}
# @inputFileName: e-merged .txt file that contains MRI output data.
# @outputDirectoryName: where you want the output files to be created. If not provided, the output directory will be created inside the directory that runs the script.

import os
import sys
import shutil

# check number of arguments
if len(sys.argv) < 2: 
	print("Error: too few arguments! ")
	print("Format is: python " + sys.argv[0] + " {e-MergedTxtFile} {OPTIONAL: outputDirectoryPath}")
	sys.exit()
elif len(sys.argv) > 3: 
	print("Error: too many arguments! ")
	print("Format is: python " + sys.argv[0] + " {e-MergedTxtFile} {OPTIONAL: outputDirectoryPath}")
	sys.exit()

# reading arguments
inputFileName = sys.argv[1]
if len(sys.argv) == 2:
	# output directory not given
	outputDirPath = os.getcwd()
elif len(sys.argv) == 3:
	# output directory given
	outputDirPath = sys.argv[2]

# check format of arguments
if not inputFileName.endswith(".txt"):
	print("Error: input must be a merged text file!")
	sys.exit()
if os.path.exists(outputDirPath):
	if not os.path.isdir(outputDirPath):
		# Path exists, but is not a directory
		print("Error: output path must be a directory!")
		sys.exit()
else: 
	print("Error: output path does not exist!")
	sys.exit()


#DEBUGGING:
print("inputFileName: " + inputFileName)
print("outputDirPath: " + outputDirPath)


columnNames = [] # found in the first row of file
data = [] # nested array of all data starting from the second row

# returns rows in which the entry in column {col} changes.
def getColChanges(col,cols,data):
	index=cols.index(col) # {index} = the index of object {col} in the list {cols}.
	output=[]
	prev = ""
	for row in xrange(len(data)): #for the specified column {index}, go down the rows and append the row number to {output} if the element curr is different from the one above it.
		curr = data[row][index]
		if curr != prev: 		
			output.append(row)
			prev = curr	#for the next comparison
	return output

# time elapsed since true zero in ms
def convertTime(onset, trueZero):	
  return str(float(int(onset)-trueZero)/1000)

#collecting all data for all subjects into array
inputFile = open(inputFileName, 'r')
for index,line in enumerate(inputFile.readlines()):	#inputFile.readLines() = a list of all lines in inputFile. 
	if index == 0:
		columns = [x.strip() for x in line.split('\t')] #sets {columns} as a list of the categories listed on the first line (separated by tabs). Strips each category of whitespace.
	else:
		data.append([x.strip() for x in line.split('\t')]) #appends an array of all the contents of {line} (separated by whitespace) to {data}. Strips whitespace.
inputFile.close()

print(columns)

# read lines into subject array based on subjectID. Each entry in this array contains all data for that subject.
Subjects = []
subjChanges=getColChanges('Subject',columns,data) #get the lines in which the Subject name changes. That way, we can separate the data lines by Subject 
for change in xrange(len(subjChanges)):		#one append for each Subject (the number of Subjects = len(subjChanges))
	if change == len(subjChanges)-1:		#if {change} is at the end of {subjChanges}
		Subjects.append(data[subjChanges[change]:])	#append the last lines of {subjChanges} as an array to {Subjects}
	else:
		Subjects.append(data[subjChanges[change]:subjChanges[change+1]])	#otherwise, append an array of the lines of the current subject until the line in which Subject changes, which is subjChanges[change]+1 to subjChanges[change+1], to {Subjects}

count = 0
# note: Subject is an array of lines of data for that subject.
# So, Subject[0] is the first line, and Subject[0][col...] is the entry in that line where the ID is.
for Subject in Subjects:
# creating output files for each subject, including instruction times, fixation times,
# times for each emotion under each question condition, and misses.
	count = count+1
	SubjID = Subject[0][columns.index('Subject')] 
	SubjID = "0" + SubjID # inserts a 0 before the first character. Ex: 5276 becomes 05276.

	try:
		print ("getting data for Subj "+SubjID)

		popFile = open(outputDirPath+"/"+SubjID+"_pop.1D",'w')
		unpFile = open(outputDirPath+"/"+SubjID+"_unp.1D",'w')
		newFile = open(outputDirPath+"/"+SubjID+"_new.1D",'w')
		rptFile = open(outputDirPath+"/"+SubjID+"_rpt.1D",'w')

		trueZeroIndex = columns.index("Symbol.TargetOnsetTime")
		trueZero = int(Subject[0][trueZeroIndex])
		trials = getColChanges("Running[Trial]", columns, Subject)
		onlyOneTrial = False # True when there is only one trial.
		if (len(trials) == 1):
			print("Error: Only Trial2 found for subject: " + SubjID)
			onlyOneTrial = True
		# Writing to all files
		onsetIndex = columns.index("Symbol.OnsetTime")
		descriptionIndex = columns.index("Description")
		if onlyOneTrial == True:
			for row in range(0,len(Subject)):
				# write to first row
				onsetTime = convertTime(Subject[row][onsetIndex], trueZero)
				description = Subject[row][descriptionIndex]
				if description == "Pop":
					popFile.write(onsetTime + "\t")
				elif description == "Unp":
					unpFile.write(onsetTime + "\t")
				elif description == "New":
					newFile.write(onsetTime + "\t")
				elif description == "Rpt":
					rptFile.write(onsetTime + "\t")

			popFile.close()
			unpFile.close()
			newFile.close()
			rptFile.close()
		else:
			taskIndex = columns.index("Running[Trial]")
			if Subject[0][taskIndex] == "SocTask1":
				range1 = [0,trials[1]]
				range2 = [trials[1],len(Subject)]
				trueZero1 = int(Subject[0][trueZeroIndex])
				trueZero2 = int(Subject[trials[1]][trueZeroIndex])
			else:
				range1 = [trials[1],len(Subject)]
				range2 = [0,trials[1]]
				trueZero1 = int(Subject[trials[1]][trueZeroIndex])
				trueZero2 = int(Subject[0][trueZeroIndex])
			for row in range(range1[0],range1[1]):
				# first task, first row.
				onsetTime = convertTime(Subject[row][onsetIndex], trueZero1)
				description = Subject[row][descriptionIndex]
				if description == "Pop":
					popFile.write(onsetTime + "\t")
				elif description == "Unp":
					unpFile.write(onsetTime + "\t")
				elif description == "New":
					newFile.write(onsetTime + "\t")
				elif description == "Rpt":
					rptFile.write(onsetTime + "\t")

			popFile.write("\n")
			unpFile.write("\n")
			newFile.write("\n")
			rptFile.write("\n")

			trueZero = int(Subject[trials[1]][trueZeroIndex])
			for row in range(range2[0],range2[1]):	
				# write to first row
				onsetTime = convertTime(Subject[row][onsetIndex], trueZero2)
				description = Subject[row][descriptionIndex]
				if description == "Pop":
					popFile.write(onsetTime + "\t")
				elif description == "Unp":
					unpFile.write(onsetTime + "\t")
				elif description == "New":
					newFile.write(onsetTime + "\t")
				elif description == "Rpt":
					rptFile.write(onsetTime + "\t")
			
			popFile.close()
			unpFile.close()
			newFile.close()
			rptFile.close()
	except ValueError:	# throw exception if integer casting fails.
		print("Failure casting value" + " (SubjID: " + SubjID + ")")

print("Number of subjects is: " + str(count))