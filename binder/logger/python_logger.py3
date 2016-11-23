# vim: set syntax=python:
import subprocess
from threading import Thread
import datetime
import time
import sys
import socket
from android import Android

msg_set=set()
stop=0
path="/storage/sdcard0/Documents/finder_logs/"
path_root="/storage/emulated/0/Documents/finder_logs/"
fname_time=datetime.datetime.now().strftime("%m%d-%H%M%S")

droid = Android()
droid.webViewShow('file:///sdcard/sl4a/scripts/index.html')

def get_log():
	logs=set()
	while 1:
		if stop:
			logs.remove("")
			with open(path+fname_time,"w") as f:
				for l in logs:
					f.write(l)
					f.write("\n")
			subprocess.call(['sort -t" "  -nk4 {}>{}'.format(path+fname_time,path+"tmp")],shell=True)
			subprocess.call(['mv {} {}'.format(path+"tmp",path+fname_time)],shell=True)
			break
		res=subprocess.check_output(['su -c "cat /sys/kernel/debug/binder/transaction_log"'],shell=True).decode().split("\r\n")
		logs.update(res)


def tcp_file_transfer(path,fname, HOST='finder.nctu.me', PORT = 8763):
    f = open(path,"rb")

    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        data = b''.join(f.readlines())
        content = b''.join([fname.encode(),":".encode(),data])
        sock.sendall(content)

    finally:
        sock.close()
        print ("Transmit complete: " + fname)

while True:
	event = droid.eventWait().result

	if event['name'] == 'start':
		global fname_time
		fname_time=datetime.datetime.now().strftime("%m%d-%H%M%S")
		stop=0
		t = Thread(target=get_log, args=())
		t.start()
		droid.makeToast('statred')
	elif event['name'] == 'stop':
		stop=1
		subprocess.call(['ps>>{}'.format(path_root+fname_time+".ps")],shell=True)
		droid.makeToast('stop')
	elif event['name'] == 'upload':
		tcp_file_transfer(path_root+fname_time,fname_time)
		tcp_file_transfer(path_root+fname_time+".ps",fname_time+".ps")
		droid.makeToast('done')
	elif event['name'] == 'exit':
		sys.exit()
