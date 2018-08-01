# ENVIRONMENT
import socket
import datetime



# BASIC VARIABLES
mepOnit = 1
meaList = []
meaCounter = 0
ueList = []
ueCounter = 0



# PORTS
mepPort = 11111
mepHost = 'mep'
buff = 1024
platformsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
platformsock.bind((mepHost, mepPort))



# LISTENING TO MEA
while mepOnit:
	platformsock.listen(5)
	print ('mep is now listening')
	conn, addr = platformsock.accept()
	requ = str(conn.recv(buff).decode())
	print('input received: ' + requ)
# APP REGISTRATION
	if requ == 'mepAva_requ':
		conn.send('mepAva_ack'.encode())
		print ('send mepAva_ack')
# APP REGISTRATION
	elif requ == 'meaReg_requ':
		conn.send('meaName_requ'.encode())
		meaName = str(conn.recv(buff).decode())
		meaList = [meaList, meaName]
		meaCounter = meaCounter + 1
		conn.send('meaReg_ack'.encode())
# UE REGISTRATION 
	elif requ == 'ueReg_requ':
		conn.send('meaName_requ'.encode())
		meaName = str(conn.recv(buff).decode())
		conn.send('ueID_requ'.encode())
		ueID = (conn.recv(buff).decode())
		ueList.append([])
		ueList[ueCounter].append(ueID)
		ueList[ueCounter].append(meaName)
		ueCounter = ueCounter + 1
		conn.send('ueReg_ack'.encode())
		print(ueList)
# UE UNSUBSCRIPTION
	elif requ == 'ueDel_requ':
		conn.send('meaName_requ'.encode())
		meaName = str(conn.recv(buff).decode())
		conn.send('ueID_requ'.encode())
		ueID = conn.recv(buff).decode()
		print(ueList)
		for ii in range(ueCounter):
			r = ueList[ii]
			print(r)
			if ueID in r:
				if meaName in r:
					del(ueList[ii])
					ueCounter = ueCounter - 1
					break
		conn.send('ueDel_ack'.encode())
		print(ueList)
# LOCATION SERVICE
	elif requ == 'location_requ':
		conn.send('location_ack'.encode())
		ueID = conn.recv(buff)
		if not ueID: 
			break
		ueID = int(ueID)
		if ueID <= 200:
			museum = "van Gogh"
		elif ueID <= 300:
			museum = "Klimt"
		elif ueID <= 400: 
			museum = "Picasso"
		else:
			museum = "error"
		conn.send(museum.encode())
# TOD SERVICE
	elif requ == 'tod_requ':
		now = datetime.datetime.now()
		conn.send(now.strftime("%Y-%m-%d %H:%M").encode())
# MEP STOP REQUEST
	elif requ == 'stop_requ':
		mepOnit = 0
	else:
		conn.send('Your requested service is unavailable at the moment.'.encode())