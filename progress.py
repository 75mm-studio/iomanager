#coding:utf8
import sys

def printBar(iteration, total):
	"""
	idx와 총 갯수를 받아, 현재의 상태를 퍼센트로 출 력해준다.
	"""
	barLength = 50
	percent = "{0:.1f}".format(100 * (iteration / float(total)))
	filledLength = int(round(barLength * iteration / float(total)))
	bar = '■' * filledLength + '_' * (barLength - filledLength)
	sys.stdout.write("\r- Progress |%s| %s%%"%( bar, percent))
	sys.stdout.flush()
	if iteration == total:
		sys.stdout.write("\33[92m  Complete \33[0m")
		sys.stdout = sys.__stdout__
