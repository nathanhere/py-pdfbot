# Authored by Nathan Nguyen, 5.26.2013

import os
import re
import subprocess

#TODO: grab linkedin ID / URL
#TODO: Scrape skills from URL
#TODO: Make classes
#TODO: Create directories for output and tmp if none exist

newline = '\n'  # \r\n for Windows compatible csv. \n is for Linux

txtDir = 'tmp/'
csvPath = 'output/profiles.csv'
pdfDir = 'pdfInput/'
countryPath = 'ref/allcountries.csv'

profiles = []


# This loop is used for individual pdf profiles.
def convert_pdf_to_txt(sourcePath, destDir):
	pdfList = os.listdir(pdfDir)
	for pdf in pdfList:
		filetxt = pdf[:len(pdf) - 4] + '.txt'
		subprocess.call(["pdftotext", sourcePath + pdf, destDir + filetxt])


# Use the line below if profiles are all in one continuous pdf:
# subprocess.call(["pdftotext",file,'pdf/' + filetxt])


def loadcountries(filename):
	with open(filename, 'r') as f:
		c = f.read()
	return c.split(',')


def writeCSVfile(filename=None, newFile=False, *args):
	if newFile:
		mode = 'w'
	else:
		mode = 'a'
	try:
		with open(filename, mode) as f:
			f.write(';'.join(args) + newline)  # \r\n is for Windows. \n is for Linux
	except:
		print 'filename or argument error'
	return


def get_location(s):
	currentPos = -1
	x = 0
	while x < 2:  # (Location info is located on line 2 of PDF linkedin resumes)
		endPos = s.find(newline, currentPos + 1)
		startPos = currentPos + 1
		currentPos = endPos
		x += 1
	location = s[startPos:endPos].strip()
	locationSplit = location.split(',')
	locationCount = len(locationSplit)
	#print locationSplit

	# Various checks to determine if city or country
	# TODO: automatically associate a country with a city if city was the only
	#		data specified
	if locationSplit[len(locationSplit) - 1].strip() in countries:
		country = locationSplit[len(locationSplit) - 1].strip()
		city = 'Not Specified'
	else:
		country = 'Not Specified'
		city = locationSplit[len(locationSplit) - 1].strip()

	if locationCount > 1:
		city = locationSplit[len(locationSplit) - 2].strip()

	#print 'city: {0}'.format(city)
	#print 'country: {0}'.format(country)
	return {'city': city, 'country': country}


def get_name(s):
# Input: string extracted from a whole pdf file
# Output: tuple of firstname and lastname from text file
	middlename = ''
	commaCount = 0
	fullname = s[:s.find(newline)]
	spaceCount = fullname.count(' ')
	commaCount = fullname.count(',')

	if commaCount:
		commaPos = fullname.find(',')
		fullname = fullname[:commaPos - 1]

	if spaceCount == 1:
		spacePos = fullname.find(' ')
		firstname = fullname[:spacePos]
		middlename = ''
		lastname = fullname[spacePos + 1:]
	else:
		fullnameList = fullname.split(' ')
		firstname = fullnameList[0]

		# test for 'van'-type last names
		if fullnameList[1].islower():
			fullnameList[len(fullnameList) - 1] = fullnameList[1] + ' ' + fullnameList[len(fullnameList) - 1]

		lastname = fullnameList[len(fullnameList) - 1]
		fullnameList.pop(len(fullnameList) - 1)
		fullnameList.pop(0)
		middlename = ' '.join(fullnameList)

	#print 'firstname: {0}'.format(firstname)
	#print 'middlename: {0}'.format(middlename)
	#print 'lastname: {0}'.format(lastname)
	return {'firstname': firstname, 'middlename': middlename, 'lastname': lastname}


def get_title(s):
	currentPos = -1
	x = 0
	# use location line as a positional reference to grab the title underneath of it
	while x < 2:  # (Location info is located on line 2 of PDF linkedin resumes)
		endPos = s.find(newline, currentPos + 1)
		startPos = currentPos + 1
		currentPos = endPos
		x += 1

	startPos = endPos + len(newline)
	endPos = s.find('\n\n')
	title = s[startPos:endPos]
	title = title.replace('\n', ' ')
	return {'title': title}


def load_profiles_to_dict(destDir):
	# Takes destination directory as input and updates a list of dicts with profile info
	txtFileList = os.listdir(destDir)

	if txtFileList:
		x = 0
		for txtFile in txtFileList:
			with open(destDir + txtFile, 'r') as f:
				s = f.read()
			profiles.append(get_name(s))
			profiles[x].update(get_title(s))
			profiles[x].update(get_location(s))
			x += 1
	else:
		print 'No txt files were found in the directory "{0}"'.format(destDir)


def write_profiles(profPath):
# Takes a profile path (string) as input and appends the csv file located there with data from the profiles list/dicts
	for profile in profiles:
		firstname = profile['firstname']
		lastname = profile['lastname']
		title = profile['title']
		city = profile['city']
		country = profile['country']
		URL = 'http://'
		writeCSVfile(profPath, False, firstname, lastname, title, city, country, URL)


batchOption = ''
RE = re.compile('[i]|[m]')

while batchOption == '':
	print "Scrape info from list of individual pdf's (i) or one pdf with multiple entries (m)?"
	batchOption = raw_input()
	if RE.match(batchOption) is None:
		batchOption = ''
		print 'You did not enter a valid option (i/m)'

# Load a list of all the countries of the world into memory
countries = loadcountries(countryPath)

# Convert individual PDF's to text files
convert_pdf_to_txt(pdfDir, txtDir)

#---------- EDIT BELOW THIS LINE ----------------

# Create CSV column titles
writeCSVfile(csvPath, True, 'firstname', 'lastname', 'title', 'city', 'country', 'URL')

# Prep profile information into memory
load_profiles_to_dict(txtDir)

# Append CSV file with profile information
write_profiles(csvPath)

print 'All data has been written to a csv file located in "{0}"'.format(csvPath)
