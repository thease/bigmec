# ENVIRONMENT
import socket
import os
import numpy
import time



# WAIT FOR MEA INSTANTIATION
time.sleep(5)



#PORTS
meaPort = 22222
meaHost = os.environ.get('meaHost', 'mea')
buff = 1024



# BASIC VARIABLES
inpOnit = 0
c = 0


# LOAD TO-DO LIST
todolist = numpy.genfromtxt('input.txt', delimiter=' ', dtype = numpy.str)



# MEA AVAILABILITY REQUEST
inp2measock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
inp2measock.connect((meaHost, meaPort))
inp2measock.send('meaAva_requ'.encode())
ack = str(inp2measock.recv(buff).decode())
if ack == 'meaAva_ack':
	print ('Application accepted')
else:
	print ('Application so: noe')
inp2measock.close()
	


# WORKING OFF THE TO-DO LIST
for c in range(len(todolist)):
	print (c)
	inp2measock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	inp2measock.connect((meaHost, meaPort))
	inp2measock.send(todolist[c][0].encode())
	print ('for c=' + str(c) + ' sent: ' + todolist[c][0])
	time.sleep(2)
	inpOnit = 1
	while inpOnit == 1:
		meaRequ = str(inp2measock.recv(buff).decode())
		print ('received: ' + meaRequ + '\n')
		time.sleep(2)
		if meaRequ == "ueID_requ":
			inp2measock.send(todolist[c][1].encode())
			print ('for c=' + str(c) + ' sent this ueID: ' + todolist[c][1])
			time.sleep(2)
		elif meaRequ == "imgURL_requ":
			inp2measock.send(todolist[c][2].encode())
			print ('for c=' + str(c) + ' sent this imgURL: ' + todolist[c][2])
			time.sleep(2)
		elif meaRequ.endswith('exhibition.'):
			time.sleep(2)
		elif meaRequ == 'imgMatch_found':
			imgData = 'reset'
			while imgData != 'end':
				print(meaRequ)
		elif meaRequ:
			print ('user request fulfilled')
			time.sleep(2)
			inpOnit = 0	
			inp2measock.close()
		else:
			print ('sorry, your request could not be fufilled. try again!')
			inpOnit = 0
			inp2measock.close()



# STOP THE SIMULATION (LIST ENDED, MEA STOP REQUEST)			
print('All desires have been fulfilled. Bye!')
inp2measock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
inp2measock.connect((meaHost, meaPort))
inp2measock.send('stop_requ'.encode())
inp2measock.close()