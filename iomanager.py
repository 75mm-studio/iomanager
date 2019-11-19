#coding:utf-8
import os
import sys
import re
import getopt
import json
import csv
import subprocess
import progress
import time

FFPROBE = "/usr/local/bin/ffmprobe"#"/storage/INHOUSE/apps/ffmpeg-4.1.4-amd64-static/ffprobe"
FFMPEG = "/usr/local/bin/ffmpeg"#"/storage/INHOUSE/apps/ffmpeg-4.1.4-amd64-static/ffmpeg"
LIBREOFFICE = "/usr/bin/soffice"
OCIO = "/Users/jyub/app/OpenColorIO-Configs/aces_1.0.3/config.ocio"
OIIOTOOL = "/usr/local/bin/oiiotool"

def findImages(path):
	"""
	경로를 받아 그 하위의 모든 폴더를 돌며 이미지 파일을 찾아 반환한다.
	"""
	print("Searching sequences...")
	fileList = []
	for rootname, _, filenames in os.walk(path):
		for filename in filenames:
			if not filename.lower().endswith((".dpx",".exr",".jpg",".jpeg",".tiff",".tif",".png",".sgi",".tga")):
				continue
			fileList.append(os.path.join(rootname,filename))
	return fileList

def fileAnalyze(fileList, path):
	"""
	파일 리스트를 받아, 멀티쓰레딩으로 파일의 정보를 분석하여 딕셔너리의 형태로 반환한다.
	"""
	print("File analyzing...")
	fileDict = {}
	startTime = time.time()
	num = 0
	for fileName in fileList:
		fileDict = seqInfo(fileName, fileDict, path)
		num += 1
		progress.printBar(num, len(fileList), startTime)
	# Add info
	for name in fileDict.keys():
		numList = map(int, fileDict[name]["numlist"])
		fileDict[name]["first"] = str(sorted(numList)[0]).zfill(fileDict[name]["seqnum"])
		fileDict[name]["last"] = str(sorted(numList)[-1]).zfill(fileDict[name]["seqnum"])
		value = fileInfo(name, fileDict[name])
		fileDict[name] = value
	return fileDict

def seqInfo(fileName, fileDict, path):
	"""
	시퀀스네임을 받아 정보를 분석하여 딕셔너리에 담는다.
	"""
	fullName, ext = os.path.splitext(fileName)
	platePath = "%s/scenes/%s/plate"%(path.split("/input/")[0], os.path.dirname(fileName).replace(path, ""))
	nameGroup = re.search("(.+)([\._])(\d+)$",fullName)
	if not nameGroup:
		name = fullName + ext
		fileDict[name] = {}
		fileDict[name]["ext"] = ext.replace(".", "")
		fileDict[name]["seqnum"] = 0
		fileDict[name]["numlist"] = [1]
		fileDict[name]["shotname"] = os.path.basename(fullName)
		fileDict[name]["platepath"] = platePath
		return
	seq = nameGroup.group(3)
	name = nameGroup.group(1) + nameGroup.group(2) + "%%0%dd"%len(seq) + ext
	if name in fileDict.keys():
		fileDict[name]["numlist"].append(seq)
	else:
		fileDict[name] = {}
		fileDict[name]["ext"] = ext.replace(".", "")
		fileDict[name]["seqnum"] = len(seq)
		fileDict[name]["numlist"] = [seq]
		fileDict[name]["shotname"] = os.path.basename(nameGroup.group(1))
		fileDict[name]["platepath"] = platePath
	return fileDict

def fileInfo(name, nameDict):
	"""
	ffprobe를 사용하여 첫프레임에서 데이터의 포멧 및 fps정보를 받아 딕셔너리로 반환한다.
	"""
	filePath = ""
	if nameDict["seqnum"]:
		pad = "%%0%dd"%nameDict["seqnum"]
		filePath = name.replace(pad, nameDict["first"]) # 첫 프레임에서 정보를 확인한다.
	else:
		filePath = name
	ffpInfo = os.popen("%s -v quiet -print_format json -show_streams %s" % (FFPROBE, filePath)).read()
	ffpInfo = eval(ffpInfo)
	if "streams" not in ffpInfo.keys():
		nameDict["width"] =  ""
		nameDict["height"] = ""
		nameDict["fps"] = ""
		return nameDict
	nameDict["width"] =  ffpInfo["streams"][0]["width"]
	nameDict["height"] = ffpInfo["streams"][0]["height"]
	nameDict["fps"] = ffpInfo["streams"][0]["r_frame_rate"].split("/")[0]
	return nameDict

def csvTask(path, dateFolder):
	"""
	csv파일을 생성하는 테스크
	"""
	err = ""
	csvFile = "%s.csv"%dateFolder
	if os.path.exists(csvFile):
		userInput = raw_input("Overwrite csv file?\n")
		if userInput not in ["y", "Y", "yes", "Yes", "YES"]:
			err = "Error - csv파일이 이미 존재합니다."
			return err
	fileList = findImages(path)
	if not fileList:
		err = "Error - 이미지 파일이 존재하지 않습니다."
		return err
	fileDict = fileAnalyze(fileList, path)
	if not fileDict:
		err = "Error - 파일 분석에 실패했습니다."
		return err
	csvSave(csvFile, fileDict, path, dateFolder)
	errList = checkData(csvFile, dateFolder)
	if errList:
		for err in errList:
			print(err)
	openOffice(csvFile)

def csvSave(csvFile, fileDict, path, dateFolder):
	"""
	csv파일의 경로와, 파일 딕셔너리를 받아, csv파일에 저장한다.
	"""
	with open(csvFile, "w") as f:
		csvW = csv.writer(f)
		csvW.writerow([
			"Input Folder Date",
			"Dirtory Folder",
			"Shot",
			"Thumbnail",
			"Format",
			"FPS",
			"ORG_In",
			"ORG_Out",
			"TW_In",
			"TW_Out",
			"Repo",
			"Camera",
			"Film Back",
			"Focal Length",
			"Assign",
			"Status",
			"Output",
			"Deadline",
			"Task",
			"Input Path",
			"Plate Path"
			])
		for name in sorted(fileDict.keys()):
			csvW.writerow([
				os.path.basename(dateFolder),
				os.path.dirname(name).replace(dateFolder, ""),
				fileDict[name]["shotname"],
				"%s/thumb/%s.jpg"%(dateFolder, fileDict[name]["shotname"]),
				"%sx%s"%(fileDict[name]["width"], fileDict[name]["height"]),
				fileDict[name]["fps"],
				fileDict[name]["first"],
				fileDict[name]["last"],
				"",
				"",
				"",
				"",
				"",
				"",
				"",
				"",
				"",
				"",
				"",
				name,
				"%s/%s"%(fileDict[name]["platepath"], fileDict[name]["ext"]),
				getIncolor(fileDict[name]["ext"])
				])

def getIncolor(ext):
	"""
	exr별 디폴트 컬러스페이스를 반환한다.
	기본은 Rec.709이다.
	"""
	incolorspace = "Output - Rec.709"
	if ext == ".exr":
		incolorspace = "Utility - Raw"
	elif ext == ".dpx":
		incolorspace = "ADX - ADX10"
	return incolorspace

def checkData(csvFile, dateFolder):
	"""
	csv파일을 받아, 이전 데이터와 비교하여 중본된 이름 또는 플레이트 파일이 있다면 에러리스트를 반환한다.
	"""
	errList = []
	prjCsvFile = "%s/data.csv"%os.path.dirname(dateFolder)
	if not os.path.exists(csvFile):
		return errList
	prjData = importCSV(prjCsvFile)
	if not prjData:
		return errList
	nameList = []
	plateList = []
	for prjLine in prjData:
		nameList.append(prjLine[2])
		plateList.append(prjLine[20])
	data = importCSV(csvFile)
	for line in data:
		name = line[2]
		platePath = line[20]
		if name in nameList:
			errList.append("Error - 중복된 샷 네임이 존재합니다. %s"%name)
		if platePath in plateList:
			errList.append("Error - 중복된 plate 파일이 존재합니다. %s"%platePath)
	return errList

def openOffice(csvFile):
	"""
	office 파일을 실행한다.
	"""
	# open csvFile
	try:
		subprocess.Popen([LIBREOFFICE,"--calc",csvFile])
	except:
		print("libreoffice5.4를 실행 할 수 없습니다. 수동으로 파일을 열어주세요.\n%s"%csvFile)

def importCSV(csvFile):
	"""
	Import csv file.
	"""
	data = []
	if not os.path.exists(csvFile):
		return data
	with open(csvFile, "r") as f:
		for line in csv.reader(f):
			data.append(line)
	del data[0] # Remove first row -> "Show, Name, ...."
	return data

def mkDataList(data):
	"""
	csv에서 불러온 list형태의 정보들 중 필요한 데이터를 찾아 딕셔너리로 반환한다.
	"""
	print("Making data list...")
	dataDict = {}
	for line in data:
		origin = line[19]
		platePath = line[20]
		first = int(line[6])
		last = int(line[7])
		if first == 1 and last == 1:
			dataDict[origin] = platePath
			continue
		frame = first
		for f in range(last -first + 1):
			dataDict[origin%frame] = platePath
			frame += 1
	return dataDict

def prjCsvSave(data, dateFolder):
	"""
	파일 데이터를 받아, 통합 csv파일에 저장한다.
	"""
	prjData = []
	csvFile = "%s/data.csv"%os.path.dirname(dateFolder)
	if os.path.exists(csvFile):
		data = importCSV(csvFile)
	prjData += data
	with open(csvFile, "w") as f:
		csvW = csv.writer(f)
		csvW.writerow([
			"Input Folder Date",
			"Dirtory Folder",
			"Shot",
			"Thumbnail",
			"Format",
			"FPS",
			"ORG_In",
			"ORG_Out",
			"TW_In",
			"TW_Out",
			"Repo",
			"Camera",
			"Film Back",
			"Focal Length",
			"Assign",
			"Status",
			"Output",
			"Deadline",
			"Task",
			"Input Path",
			"Plate Path"
			])
		for line in prjData:
			csvW.writerow(line)

def copyTask(dataDict, path):
	"""
	데이터를 복사한다.
	"""
	print("Copying...")
	errList = []
	startTime = time.time()
	num = 0
	for trgt in dataDict.keys():
		errList = copyFiles(trgt, dataDict[trgt], errList)
		num += 1
		progress.printBar(num, len(dataDict.keys()), startTime)
	# save Error log
	if errList:
		errLog = {}
		errLog["copylog"] = errList
		print("Error - Error occurs during the copy process.")
		saveLog(path, errLog)

def copyFiles(trgt, dstFolder, errList):
	"""
	폴더를 생성하고, 데이터를 복사한다.
	"""
	# Make dirs
	try:
		os.system("mkdir -p %s"%dstFolder)
	except Exception as e:
		errList.append("Error - %s"%e)
	# Copy files
	try:
		os.system("cp -f %s %s"%(trgt, dstFolder))
	except Exception as e:
		errList.append("Error - %s"%e)

def thumbTask(data, path):
	"""
	멀티쓰레드를 이용하여 썸네일을 생성한다.
	"""
	print("Creating thumbnails...")
	errList = []
	startTime = time.time()
	num = 0
	for line in data:
		errList = createThumb(line, errList)
		num += 1
		progress.printBar(num, len(data), startTime)
	# save Error log
	if errList:
		errLog = {}
		errLog["thumblog"] = errList
		print("Error - Error occurs during making thumbnail process.")
		saveLog(path, errLog)

def createThumb(line, errList):
	"""
	ffmpeg를 사용하여 썸네일을 생성한다.
	에러가 발생되면 에러리스트에 추가한다.
	"""
	origin = line[19]
	first = int(line[6])
	last = int(line[7])
	thumbPath = line[3]
	fmt = line[4]
	if first == 1 and last == 1:
		orgPlate = origin
	else:
		orgPlate = origin%(first + ((last - first) / 2)) # Use middle frame
	width = int(fmt.split("x")[0]) / 10 # 1/10 size
	thumbFolder = os.path.dirname(thumbPath)
	# Make dirs
	try:
		os.system("mkdir -p %s"%thumbFolder)
	except Exception as e:
		errList.append("Error - %s"%e)
	# Make thumbnail
	try:
		os.system("export OCIO=%s && %s --frame %s %s --colorconvert %s %s --resize %sx0 -o %s"%(OCIO, OIIOTOOL, frame, orgPlate, incolorspace, outcolorspace, width/10, thumbPath))
	except Exception as e:
		errList.append("Error - ffmpeg : %s"%e)
	return errList

def saveLog(path, errLog):
	"""
	경로와 에러로그를 받아, json으로 저장한다.
	기존에 json이 있다면 업데이트한다.
	"""
	log = {}
	logJson = "%s.json"%path
	if os.path.exists(logJson):
		with open(logJson) as f:
			log = json.load(f)
	log.update(errLog)
	with open(logJson, "w") as f:
		json.dump(log, f, indent=4, ensure_ascii=False)

def makeXlsx(csvFile):
	"""
	생성된 csv파일을 이용해 xlsx파일을 생성한다.
	컨버팅된 썸네일 이미지를 xlsx파일에 삽입한다.
	"""
	print("Creating xlsx...")
	import xlsxwriter
	# Import Data
	data = []
	with open(csvFile, "r") as f:
		for line in csv.reader(f):
			data.append(line)
	# Create an new Excel file and add a worksheet.
	workbook = xlsxwriter.Workbook(csvFile.replace(".csv", ".xlsx"))
	worksheet = workbook.add_worksheet()
	# Create format
	firstRowFormat = workbook.add_format({"bold": True})
	firstRowFormat.set_align("center")
	firstRowFormat.set_align("vcenter")
	cell_format = workbook.add_format()
	cell_format.set_align("center")
	cell_format.set_align("vcenter")
	# Set width, height
	widthDict = {}
	imgWidth, imgHeight = 0, 0
	if "x" in data[1][4]:
		imgWidth, imgHeight = data[1][4].split("x") # get Image Size, Use first image as sample
	row = 0
	for line in data:
		col = 0
		for value in line:
			# Set width
			thisWidth = len(value)
			widthDict = getColumnWidth(widthDict, col, thisWidth)
			worksheet.set_column(col, col, widthDict[col])
			# Set item
			if row == 0: # First row
				worksheet.write(row, col, value, firstRowFormat)
			elif col == 3: # thumbnail
				if not os.path.exists(value):
					print("Error : Thumbnail is not exists : %s"%value)
					continue
				worksheet.insert_image(row, col, value)
				worksheet.set_row(row, int(imgHeight)/13) # thumbnail 이미지는 1/10이다. 대략 13으로 나누어야 높이가 맞는다.
			else:
				worksheet.write(row, col, value, cell_format)
			col += 1
		row += 1

	worksheet.set_column(3, 3, int(imgWidth)/70) # 대략 70으로 나누어야 넓이가 맞는다.
	workbook.close()

def getColumnWidth(widthDict, col, thisWidth):
	"""
	텍스트의 가로 길이와, 해당 컬럼, 컬럼별 가로길이가 포함된 딕셔너리를 받아,
	가장 넓은 가로 길이를 반환한다.
	"""
	if col not in widthDict.keys():
		widthDict[col] = thisWidth
		return widthDict
	if thisWidth > widthDict[col]:
		widthDict[col] = thisWidth
		return widthDict
	return widthDict


def makeProxy():
	cmd = "export OCIO=%s && %s --frame %s-%s %s --colorconvert %s %s -o %s"%(OCIO, OIIOTOOL, first, last, inputfile, incolorspace, outcolorspace, outfile)

def makeMov():
	cmd = "%s -r 24 -f image2 -start_number %s -i %s -c:v libx264 -pix_fmt yuv420p %s"%(FFMPEG, first, inputfile, outfile)

def help():
	print(
"""
ioManager V1.8 - I/O Management Tool

-h, --help : Help
	$ iomanager -h
-p, --path : 사용자가 폴더를 직접 입력합니다.
	$ iomanager -p /show/PROJECT/input/DATE
-v, --csv : 해당 폴더 또는 사용자가 입력한 폴더에서 시퀀스를 분석하여 csv파일을 생성합니다.
	$ iomanager -v
-c, --copy : 해당 폴더 또는 사용자가 입력한 폴더의 이름을 가진 csv 데이터로 "/show/PROJECT/scenes" 하위에 복사합니다. plate 및 ext이름의 폴더가 생성되며, thumbnail과 mov를 생성합니다.
	$ iomanager -c
-t, --thumb : 해당 폴더 또는 사용자가 입력한 폴더의 이름을 가진 csv 데이터로 약속된 폴더에 thumbnail을 생성합니다.
	$ iomanager -t
-m, --mov : 해당 폴더 또는 사용자가 입력한 폴더의 이름을 가진 csv 데이터로 약속된 폴더에 mov를 생성합니다.
	$ iomanager -m
-x, --xlsx : 해당 폴더 또는 사용자가 입력한 폴더의 이름을 가진 csv 데이터로 xlsx 파일을 생성합니다.
	$ iomanager -x
"""
	)

def main():
	"""
	특정 경로 하위의 모든 시퀀스를 찾아 분석하여, 복사 및 썸네일을 생성하는 툴이다.
	"""
	opts, args = getopt.getopt(sys.argv[1:], "p:vctmxh",["path=", "csv", "copy", "thumb", "mov", "xlsx", "help"])
	if len(opts) == 0 and len(args) == 0 :
		help()
		sys.exit(1)
	path = os.getcwd()
	csv = False
	copy = False
	thumb = False
	mov = False
	xlsx = False
	for key, value in opts :
		if key in ("-h", "--help"):
			help()
			sys.exit()
		elif key in ("-p", "--path"):
			path = value
		elif key in ("-v", "--csv"):
			csv = True
		elif key in ("-c", "--copy"):
			copy = True
		elif key in ("-t", "--thumb"):
			thumb = True
		elif key in ("-m", "--mov"):
			thumb = True
		elif key in ("-x", "--xlsx"):
			xlsx = True
		else:
			"Check Option '-h, --help'"
			return
	if not path.endswith("/"):
		path += "/"
	regx = re.search("/show/.+/input/(\d+)", path)
	if not regx:
		print("Error - 약속된 경로가 아닙니다. ex) /show/PROJECT/input/DATE/")
		sys.exit(1)
	dateFolder = regx.group(1)
	dateFolder = path.split("/input/%s"%dateFolder)[0] + "/input/" + dateFolder
	if not csv and not copy and not thumb and not xlsx:
		help()
		sys.exit(1)
	if csv:
		err = csvTask(path, dateFolder)
		if err:
			print(err)
			sys.exit(1)
	if copy:
		csvFile = "%s.csv"%dateFolder
		if not os.path.exists(csvFile):
			print("Error - no CSV")
			sys.exit(1)
		data = importCSV(csvFile)
		if not data:
			print("Error - no CSV data.")
			sys.exit(1)
		prjCsvSave(data, dateFolder)
		dataDict = mkDataList(data)
		copyTask(dataDict, path)
		thumbTask(data, path)
		movTask(data, path)
	if thumb:
		csvFile = "%s.csv"%dateFolder
		data = importCSV(csvFile)
		if not data:
			print("Error - no CSV data.")
			sys.exit(1)
		thumbTask(data, path)
	if mov:
		csvFile = "%s.csv"%dateFolder
		data = importCSV(csvFile)
		if not data:
			print("Error - no CSV data.")
			sys.exit(1)
		movTask(data, path)
	if xlsx:
		csvFile = "%s.csv"%dateFolder
		if not os.path.exists(csvFile):
			print("Error - no CSV")
			sys.exit(1)
		makeXlsx(csvFile)

if __name__ == "__main__":
	main()
