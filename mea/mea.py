# ENVIRONMENT
import sys
import cv2
import os
from google_drive_downloader import GoogleDriveDownloader as gdd
import shutil
import urllib.request
import tempfile
import socket
import time



# WAIT FOR MEP INSTANTIATION
time.sleep(5)



# BASIC VARIABLES
meaOnit = 1
stopCount = 0



# PORTS
meaPort = 22222
meaHost = 'mea'
mepPort = 11111
mepHost = os.environ.get('mepHost', 'mep')
buff = 1024
measock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
measock.bind((meaHost, meaPort))
mepAva = 0
meaReg = 0



# MEP AVAILABILITY REQUEST
while mepAva == 0:
	mea2mepsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	mea2mepsock.connect((mepHost, mepPort))
	mea2mepsock.send('mepAva_requ'.encode())
	print ('sent mepAva_requ')
	ack = str(mea2mepsock.recv(buff).decode())
	print ('received: ' + ack)
	if ack == "mepAva_ack":
		print ('MEP is available.')
		mepAva = 1
	else:
		print('MEP is not available.')
	mea2mepsock.close()

	
	
# REGISTRATION AT MEP
while meaReg == 0:
	mea2mepsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	mea2mepsock.connect((mepHost, mepPort))
	mea2mepsock.send('meaReg_requ'.encode())	
	print ('sent meaReg_requ')
	ack = str(mea2mepsock.recv(buff).decode())
	if ack == "meaName_requ":
		mea2mepsock.send('MuseumAR'.encode())
		print ('sent App Name')
		ack = str(mea2mepsock.recv(buff).decode())
		if ack == 'meaReg_ack':
			print ('Application is registered.')
			meaReg = 1
			break
		else:
			print ('App could not be registered (no meaReg_ack).')
	else:
		print ('App could not be registered (no meaName_requ.')
	mea2mepsock.close()


# TEMPORARY DIRECTORIES
try:
	temPath = tempfile.gettempdir()
	if os.path.exists(temPath+"/museumsapp"):
		shutil.rmtree((temPath+"/museumsapp/"), ignore_errors=True)
	os.makedirs(temPath+"/museumsapp/user/")
	os.makedirs(temPath+"/museumsapp/templates/")
	userImgDir = (temPath+"/museumsapp/user/userImg.png")
	templateDir = (temPath+"/museumsapp/templates/")
except: print ('Could not create the directory!')



# LISTENING TO UE INPUT
while meaOnit:
	measock.listen(5)
	print ('mea is now listening')
	conn, addr = measock.accept()
	inpRequ = str(conn.recv(buff).decode())
	print('received ' + inpRequ)
# MEA AVAILABILITY
	if inpRequ == 'meaAva_requ':
		conn.send('meaAva_ack'.encode())
# UE REGISTRATION
	elif inpRequ == 'ueReg_requ':
		conn.send("ueID_requ".encode())
		ueID = str(conn.recv(buff).decode())
		mea2mepsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		mea2mepsock.connect((mepHost, mepPort))
		mea2mepsock.send('ueReg_requ'.encode())
		ack = str(mea2mepsock.recv(buff).decode())
		if ack == 'meaName_requ':
			mea2mepsock.send('MuseumAR'.encode())
			ack = str(mea2mepsock.recv(buff).decode())
			if ack == 'ueID_requ':
				mea2mepsock.send(ueID.encode())
				ack = str(mea2mepsock.recv(buff).decode())
				if ack == 'ueReg_ack':
					conn.send('ueReg_ack'.encode())
				else:
					conn.send('UE could not be registered. (no regist_ack)'.encode())
			else:
				conn.send('UE could not be registered. (no ueID_requ)'.encode())
		else:
			conn.send('UE could not be registered. (no meaName_requ)'.encode())
		mea2mepsock.close()
# UE UNSUBSCRIPTION
	elif inpRequ == 'ueDel_requ':
		conn.send("ueID_requ".encode())
		ueID = str(conn.recv(buff).decode())
		mea2mepsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		mea2mepsock.connect((mepHost, mepPort))
		mea2mepsock.send('ueDel_requ'.encode())
		ack = str(mea2mepsock.recv(buff).decode())
		if ack == 'meaName_requ':
			mea2mepsock.send('MuseumAR'.encode())
			ack = str(mea2mepsock.recv(buff).decode())
			if ack == 'ueID_requ':
				mea2mepsock.send(ueID.encode())
				ack = str(mea2mepsock.recv(buff).decode())
				if ack == 'ueDel_ack':
					conn.send('UE is deleted.'.encode())
				else:
					conn.send('UE could not be deleted. (no delet-ack)'.encode())
			else:
				conn.send('UE could not be deleted. (no ueId-requ)'.encode())
		else:
			conn.send('UE could not be deleted. (no meaName_requ)'.encode())
		mea2mepsock.close()
# IMAGE REQUEST
	elif inpRequ == 'img_requ':
		conn.send("imgURL_requ".encode())
		userImgUrl = str(conn.recv(buff).decode())
		testfile = urllib.request.URLopener()
		testfile.retrieve(userImgUrl, userImgDir)
		userImg = cv2.imread(userImgDir)
# MUSEUM LOCALIZATION
		conn.send("ueID_requ".encode())
		ueID = int(conn.recv(buff).decode())
		mea2mepsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		mea2mepsock.connect((mepHost, mepPort))
		mea2mepsock.send('location_requ'.encode())
		ack = str(mea2mepsock.recv(buff).decode())
		if ack == 'location_ack':
			mea2mepsock.send(str(ueID).encode())
			exhibition = str(mea2mepsock.recv(buff).decode())
			exInfo = 'You are at the ' + exhibition + ' exhibition. \n'
			conn.send(exInfo.encode())
		else:
			print ('Localization service is unavailable.')
		mea2mepsock.close()
		if exhibition == "van Gogh":
			urlDir = "1GOXwGs7zp9IMT79nD9mPfUxVifEhY3hH"
		elif exhibition == "Klimt":
			urlDir = "1Y4CAZkN0MHzVaK9VAKnvkhGEzf3nUJlm"
		elif exhibition == "Picasso":
			urlDir = "1QjGMj6WK2cSHKzUJW21cc4RLr8vIvvGx"
# GET EXHIBITION'S TEMPLATES
		print ('getting the templates')
		mustempDir = templateDir+str(exhibition)+'/'
		gdd.download_file_from_google_drive(file_id=urlDir, dest_path=mustempDir+str(exhibition)+".zip", unzip=True)
		templSet = []
		valid_image_extensions = [".jpg", ".jpeg", ".png", ".tif", ".tiff"] 
		valid_image_extensions = [item.lower() for item in valid_image_extensions]
		for file in os.listdir(mustempDir):
			extension = os.path.splitext(file)[1]
			if extension.lower() not in valid_image_extensions:
				continue
			templSet.append(os.path.join(mustempDir, file))
# IMAGE MATCHING
		print ('start matching')
		bestmatch = 0
		bestTmRes = 0
		for templPath in templSet:
			templ = cv2.imread(templPath)
			height, width = templ.shape[:2]
			tmRes = cv2.matchTemplate(userImg, templ, cv2.TM_CCOEFF)
			(_, maxVal, _, maxLoc) = cv2.minMaxLoc(tmRes)
			maxVal = maxVal/height/width
			if maxVal > bestTmRes:
				bestTmRes = maxVal
				bestmatch = templPath
# IMAGE DATA TO UE
		if bestTmRes < 3000:
			conn.send("Couldn't match your pic, sorry. Please try again!".encode())
		else:
			conn.send("imgMatch_found".encode())
			myfile = open(os.path.splitext(bestmatch)[0]+'.txt',"r")
			lines = myfile.readlines()
			for line in lines:
				imgInfo = line.strip() + ' \n'
				conn.send(imgInfo.encode())
				print ('sent: ' + line.strip())
			conn.send('end'.encode())
# MEA STOP REQUEST
	elif inpRequ == 'stop_requ':
		meaOnit = 0
	else:
		stopCount += 1
		if stopCount == 3:
			meaOnit = 0
conn.close()



# MEP STOP REQUEST
mea2mepsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mea2mepsock.connect((mepHost, mepPort))
mea2mepsock.send('stop_requ'.encode())
mea2mepsock.close()



# DELETE TEMPORARY APP DIRECTORIES
shutil.rmtree((temPath+"/museumsapp/"), ignore_errors=True)
