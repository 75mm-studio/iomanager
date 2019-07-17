#coding:utf-8
import os
import sys
import re
import getopt
import json
import csv
import subprocess
import threading
import progress

SEM = 2
FFPROBE = "/usr/local/bin/ffprobe"
FFMPEG = "/usr/local/bin/ffmpeg"
LIBEROOFFICE = "/opt/libreoffice5.4/program/soffice"

def findImages(path):
	"""
	경로를 받아 그 하위의 모든 폴더를 돌며 이미지 파일을 찾아 반환한다.
	"""
	print("Searching sequences...")
	fileList = []
	for rootname, _, filenames in os.walk(path):
		for filename in filenames:
			if not filename.endswith((".dpx",".exr",".jpg",".jpeg",".tiff",".tif")):
				continue
			fileList.append(os.path.join(rootname,filename))
	return fileList

def fileAnalyze(fileList, path):
	"""
	파일 리스트를 받아, 멀티쓰레딩으로 파일의 정보를 분석하여 딕셔너리의 형태로 반환한다.
	"""
	print("File analyzing...")
	# Use multi thread
	lock = threading.Lock()
	sem = threading.Semaphore(SEM)
	threads = []
	fileDict = {}
	for fileName in fileList:
		lock.acquire()
		t = threading.Thread(target=seqInfo, args=(fileName, fileDict, path, sem))
		t.start()
		lock.release()
		threads.append(t)
	num = 0
	for t in threads:
		num += 1
		t.join()
		progress.printBar(num,len(fileList))
	# Add info
	for name in fileDict.keys():
		numList = map(int, fileDict[name]["numlist"])
		fileDict[name]["first"] = str(sorted(numList)[0]).zfill(fileDict[name]["seqnum"])
		fileDict[name]["last"] = str(sorted(numList)[-1]).zfill(fileDict[name]["seqnum"])
		value = fileInfo(name, fileDict[name])
		fileDict[name] = value
	return fileDict

def seqInfo(fileName, fileDict, path, sem):
	"""
	시퀀스네임을 받아 정보를 분석하여 딕셔너리에 담는다.
	"""
	sem.acquire()
	fullName, ext = os.path.splitext(fileName)
	platePath = "%s/scenes%s/plate"%(path.split("/input/")[0], os.path.dirname(fileName).split(path)[1])
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
	sem.release()

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

def csvTask(path):
	"""
	csv파일을 생성하는 테스크
	"""
	err = ""
	csvFile = "%s.csv"%path
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
	csvSave(csvFile, fileDict, path)
	openOffice(csvFile)

def csvSave(csvFile, fileDict, path):
	"""
	csv파일의 경로와, 파일 딕셔너리를 받아, csv파일에 저장한다.
	"""
	dateFolder = os.path.basename(path)
	with open(csvFile, "w") as f:
		csvW = csv.writer(f)
		csvW.writerow([
			"Input Folder Date",
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
		for name in fileDict.keys():
			csvW.writerow([
				dateFolder,
				fileDict[name]["shotname"],
				"%s/thumb/%s.jpg"%(path, fileDict[name]["shotname"]),
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
				"%s/%s"%(fileDict[name]["platepath"], fileDict[name]["ext"])
				])

def openOffice(csvFile):
	"""
	office 파일을 실행한다.
	"""
	# open csvFile
	try:
		subprocess.Popen([LIBEROOFFICE,"--calc",csvFile])
	except:
		print("libreoffice5.4를 실행 할 수 없습니다. 수동으로 파일을 열어주세요.\n%s"%csvFile)

def importCSV(csvFile):
	"""
	Import csv file.
	"""
	data = []
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
		origin = line[18]
		platePath = line[19]
		first = int(line[5])
		last = int(line[6])
		if first == 1 and last == 1:
			dataDict[origin] = platePath
			continue
		frame = first
		for f in range(last -first + 1):
			dataDict[origin%frame] = platePath
			frame += 1
	return dataDict

def copyTask(dataDict, path):
	"""
	멀티쓰레드를 이용하여 데이터를 복사한다.
	"""
	print("Copying...")
	# Use multi thread
	lock = threading.Lock()
	sem = threading.Semaphore(SEM)
	threads = []
	errList = []
	for trgt in dataDict.keys():
		lock.acquire()
		t = threading.Thread(target=copyFiles, args=(trgt, dataDict[trgt], errList, sem))
		t.start()
		lock.release()
		threads.append(t)
	num = 0
	for t in threads:
		num += 1
		t.join()
		progress.printBar(num, len(dataDict.keys()))
	# save Error log
	if errList:
		errLog = {}
		errLog["copylog"] = errList
		print("Error - Error occurs during the copy process.")
		saveLog(path, errLog)

def copyFiles(trgt, dstFolder, errList, sem):
	"""
	폴더를 생성하고, 데이터를 복사한다.
	"""
	sem.acquire()
	# Make dirs
	proc = subprocess.Popen(["mkdir -p %s"%dstFolder], stdout = subprocess.PIPE,  stderr = subprocess.PIPE, shell=True)
	stdout, stderr = proc.communicate()
	if stderr:
		errList.append("Error - %s"%stderr)
	# Copy files
	proc = subprocess.Popen(["cp -f %s %s"%(trgt, dstFolder)], stdout = subprocess.PIPE,  stderr = subprocess.PIPE, shell=True)
	stdout, stderr = proc.communicate()
	if stderr:
		errList.append("Error - %s"%stderr)
	sem.release()

def thumbTask(data, path):
	"""
	멀티쓰레드를 이용하여 썸네일을 생성한다.
	"""
	print("Creating thumbnails...")
	# Use multi thread
	lock = threading.Lock()
	sem = threading.Semaphore(SEM)
	threads = []
	errList = []
	for line in data:
		lock.acquire()
		t = threading.Thread(target=createThumb, args=(line, errList, sem))
		t.start()
		lock.release()
		threads.append(t)
	num = 0
	for t in threads:
		num += 1
		t.join()
		progress.printBar(num, len(data))
	# save Error log
	if errList:
		errLog = {}
		errLog["thumblog"] = errList
		print("Error - Error occurs during the making thumbnail process.")
		saveLog(path, errLog)

def createThumb(line, errList, sem):
	"""
	ffmpeg를 사용하여 썸네일을 생성한다.
	에러가 발생되면 에러리스트에 추가한다.
	"""
	sem.acquire()
	origin = line[18]
	first = int(line[5])
	last = int(line[6])
	thumbPath = line[2]
	fmt = line[3]
	if first == 1 and last == 1:
		orgPlate = origin
	else:
		orgPlate = origin%(first + ((last - first) / 2)) # Use middle frame
	width = int(fmt.split("x")[0]) / 10 # 1/10 size
	thumbFolder = os.path.dirname(thumbPath)
	# Make dirs
	proc = subprocess.Popen(["mkdir -p %s"%thumbFolder], stdout = subprocess.PIPE,  stderr = subprocess.PIPE, shell=True)
	stdout, stderr = proc.communicate()
	if stderr:
		errList.append("Error - %s"%stderr)
	# Make thumbnail
	proc = subprocess.Popen(["%s -y -loglevel error -i %s -vf scale=%s:-1 %s"%(FFMPEG, orgPlate, width, thumbPath)],
		stdout = subprocess.PIPE, 
		stderr = subprocess.PIPE,
		shell=True)
	stdout, stderr = proc.communicate()
	if stderr:
		errList.append("Error - ffmpeg : %s"%stderr)
	sem.release()

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

def help():
	print(
"""
ioManager V1.0 - I/O Management Tool

-h, --help : Help
    $ iomanager -h
-p, --path : 사용자가 폴더를 직접 입력합니다.
    $ iomanager -p /show/PROJECT/input/DATE
-v, --csv : 해당 폴더 또는 사용자가 입력한 폴더에서 시퀀스를 분석하여 csv파일을 생성합니다.
    $ iomanager -v
-c, --copy : 해당 폴더 또는 사용자가 입력한 폴더의 이름을 가진 csv 데이터로 "/show/PROJECT/scenes" 하위에 복사합니다. plate 및 ext이름의 폴더가 생성되며, thumbnail을 생성합니다.
    $ iomanager -c
-t, --thumb : 해당 폴더 또는 사용자가 입력한 폴더의 이름을 가진 csv 데이터로 약속된 폴더에 thumbnail을 생성합니다.
    $ iomanager -t
"""
	)

def main():
	"""
	특정 경로 하위의 모든 시퀀스를 찾아 분석하여, 복사 및 썸네일을 생성하는 툴이다.
	"""
	opts, args = getopt.getopt(sys.argv[1:], "p:vcth",["path=", "csv", "copy", "thumb", "help"])
	if len(opts) == 0 and len(args) == 0 :
		help()
		sys.exit(1)
	path = os.getcwd()
	csv = False
	copy = False
	thumb = False
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
		else:
			"Check Option '-h, --help'"
	regx = re.search("/show/(.+)/input/\d+", path)
	if not regx:
		print("Error - 약속된 경로가 아닙니다. ex) /show/PROJECT/input/DATE/")
		sys.exit(1)
	project = regx.group(1)
	if not csv and not copy and not thumb:
		help()
		sys.exit(1)
	if csv:
		err = csvTask(path)
		if err:
			print(err)
			sys.exit(1)
	if copy:
		csvFile = "%s.csv"%path
		data = importCSV(csvFile)
		if not data:
			print("Error - no CSV data.")
			sys.exit(1)
		dataDict = mkDataList(data)
		copyTask(dataDict, path)
		thumbTask(data, path)
	if thumb:
		csvFile = "%s.csv"%path
		data = importCSV(csvFile)
		if not data:
			print("Error - no CSV data.")
			sys.exit(1)
		thumbTask(data, path)

if __name__ == "__main__":
	main()
